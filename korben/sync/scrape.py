import datetime
import enum
import logging
import multiprocessing
import os
import pickle
import time
import random

from requests import exceptions as reqs_excs
import sqlalchemy as sqla
from lxml import etree

from korben import config
from korben.cdms_api.rest.api import CDMSRestApi
from . import constants
from . import populate

api = None

class LoggingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('requests')


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('korben.sync.scrape')
logging.getLogger().addFilter(LoggingFilter())

try:
    with open('popular-entities', 'r') as entity_names_fh:
        ENTITY_NAMES = [name.strip() for name in entity_names_fh.readlines()]
    print('Using popular-entities file:')
    for entity_name in ENTITY_NAMES:
        print("  {0}".format(entity_name))
except FileNotFoundError:
    ENTITY_NAMES = constants.ENTITY_NAMES

PROCESSES = 32
CHUNKSIZE = 100
PAGESIZE = 50


def file_leaf(*args):
    '''
    Where *args are str, the last str is the name of a file and the preceding
    str are path fragments, create necessary and suffcient directories for the
    file to be created at the path.
    '''
    path = os.path.join(*map(str, args))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def request_cache_key(entity_name, offset):
    'Return the path where a request cache entry should be written'
    return file_leaf('cache', 'request', entity_name, offset)


def duration_record(entity_name, offset):
    'Return the path where a request duration record should be written'
    return file_leaf('cache', 'duration', entity_name, offset)


def is_cached(entity_name, offset):
    '''
    Determine if a certain request is cached, return is a 2-tup (bool, str)
    where the bool is whether or not the request is cached and the str is the
    path it either is or should be cached at.
    '''
    path = request_cache_key(entity_name, offset)
    if not os.path.isfile(path):
        return False, path
    try:
        with open(path, 'rb') as cache_fh:
            resp = pickle.load(cache_fh)
            etree.fromstring(resp.content)
    except etree.XMLSyntaxError as exc:
        return False, path
    return True, path


def cdms_list(entity_name, offset):
    '''
    Call the `cdms_api.list` method, passing through the entity_name and
    offset. This function records the duration of the network request. It also
    caches the resulting response if it’s successful and raises an informative
    exception if it’s not.
    '''
    global api
    cached, cache_path = is_cached(entity_name, offset)
    if cached:  # nothing to do, just load resp from cache
        with open(cache_path, 'rb') as cache_fh:
            return pickle.load(cache_fh)
    start_time = datetime.datetime.now()
    resp = api.list(entity_name, skip=offset)  # the actual request
    time_delta = (datetime.datetime.now() - start_time).seconds
    # carry out a healthy whack of inspection
    # it’s hairy, but that’s how we like it
    if not resp.ok:
        try:
            root = etree.fromstring(resp.content)
            if 'paging' in root.find(constants.MESSAGE_TAG).text:
                # assuming this means we tried to reach beyond the last page
                raise EntityPageNoData(
                    "500 page out {0} {1}".format(
                        entity_name, offset
                    )
                )
        except AttributeError as exc:
            # no message in xml
            raise EntityPageDynamicsBombed(
                "{0} {1}".format(entity_name, offset)
            )
        except etree.XMLSyntaxError as exc:
            # no xml in xml
            raise EntityPageDynamicsBombed(
                "{0} {1}".format(entity_name, offset)
            )
        raise RuntimeError("{0} {1} unhandled".format(entity_name, offset))
    try:
        root = etree.fromstring(resp.content)  # check XML is parseable
        if not root.findall('{http://www.w3.org/2005/Atom}entry'):
            # paged out in a useless way
            raise EntityPageNoData("{0} {1}".format(entity_name, offset))
    except etree.XMLSyntaxError as exc:
        raise EntityPageDeAuth("{0} {1}".format(entity_name, offset))
    # record our expensive network request
    with open(duration_record(entity_name, offset), 'w') as duration_fh:
        duration_fh.write(str(time_delta))
    with open(cache_path, 'wb') as cache_fh:
        pickle.dump(resp, cache_fh)
    LOGGER.info("{0} ({1}) {2}s".format(entity_name, offset, time_delta))
    return resp


class EntityPageException(Exception):
    pass


class EntityPageDynamicsBombed(EntityPageException):
    pass


class EntityPageNoData(EntityPageException):
    pass


class EntityPageDeAuth(EntityPageException):
    pass


EntityPageState = enum.Enum(
    'EntityPageState',
    (
            'initial',
#               |                                                       # NOQA
#               |                                                       # NOQA
            'pending',
#             /   \                                                     # NOQA
#            /     \                                                    # NOQA
       'failed', 'complete',
    )
)

EntityChunkState = enum.Enum(
    'EntityChunkState',
    (
           'incomplete',
#             /   \                                                     # NOQA
#            /     \                                                    # NOQA
        'spent', 'complete',
    )
)


def is_pending(entity_page):
    'Convenience function to test if an EntityPage object is in pending state'
    return entity_page.state == EntityPageState.pending


class EntityChunk(object):
    '''
    Object to manage the processing of CHUNKSIZE many EntityPage objects, these
    represent a bunch of requests that should be made to fetch data from
    Dynamics. This object basically holds the range and convenience methods for
    reporting on the state of requests.
    '''

    state = EntityChunkState.incomplete

    def __init__(self, entity_name, offset_start, offset_end):
        self.entity_name = entity_name
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.entity_pages = []
        for offset in range(offset_start, offset_end, PAGESIZE):
            # bung entity pages on to the pile
            self.entity_pages.append(EntityPage(entity_name, offset))

    def __str__(self):
        return "<EntityChunk {0} ({1}-{2})>".format(
            self.entity_name, self.offset_start, self.offset_end
        )

    def pending(self):
        'Return number of pending tasks'
        return len(list(filter(is_pending, self.entity_pages)))

    def start(self, pool):
        'Start the first "unstarted" task'
        for entity_page in self.entity_pages:
            if entity_page.state == EntityPageState.initial:
                entity_page.start(pool)
                break

    def poll(self):
        'Are all the tasks complete?'
        done = (
            entity_page.state == EntityPageState.complete
            for entity_page in self.entity_pages
        )
        if all(done):
            self.state = EntityChunkState.complete


class EntityPage(object):
    '''
    Object representing a single request to Dyanmics. Knows how to map from a
    bunch of different exceptions to state that can be examined higher up the
    call graph.
    '''

    state = EntityPageState.initial
    task = None
    entries = None
    rows_inserted = None
    exception = None

    def __init__(self, entity_name, offset):
        self.entity_name = entity_name
        self.offset = offset

    def __str__(self):
        return "<EntityPage {0} ({1})>".format(self.entity_name, self.offset)

    def reset(self):
        'Used in the case of failure where the request should be made again'
        self.state = EntityPageState.initial
        self.task = None
        self.entries = None
        self.rows_inserted = None
        self.exception = None

    def start(self, pool):
        'Send this task to the pool and store the AysyncResult object locally'
        self.task = pool.apply_async(cdms_list, (
            self.entity_name, self.offset
        ))
        self.state = EntityPageState.pending

    def poll(self):
        'Poll self.task, translate exception to state'
        if self.state == EntityPageState.initial:
            return  # not started
        if not self.task.ready():
            return  # pending
        try:
            self.task.get()
            self.state = EntityPageState.complete
        except (EntityPageNoData, EntityPageDeAuth) as exc:
            self.exception = exc
            self.state = EntityPageState.failed
        except (
            EntityPageDynamicsBombed, reqs_excs.ConnectionError, RuntimeError
        ) as exc:
            LOGGER.debug(exc)
            LOGGER.error("{0} errored, resetting".format(self))
            self.reset()


def main():
    pool = multiprocessing.Pool(processes=PROCESSES)
    entity_chunks = []
    spent_path = file_leaf('cache', 'spent')
    engine = sqla.create_engine(config.database_odata_url)
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    try:
        with open(spent_path, 'rb') as spent_fh:
            spent = pickle.load(spent_fh)
        print("Skipping {0} entity types \o/".format(len(spent)))
    except FileNotFoundError:
        spent = set()
        with open(spent_path, 'wb') as spent_fh:
            pickle.dump(spent, spent_fh)
    for entity_name in set(constants.ENTITY_NAMES) - spent:
        try:
            caches = os.listdir(os.path.join('cache', 'list', entity_name))
            start = max(map(int, caches)) + 50
        except (FileNotFoundError, ValueError) as exc:
            start = 0
        end = start + (CHUNKSIZE * PAGESIZE)
        entity_chunks.append(EntityChunk(entity_name, start, end))
    global api
    api = CDMSRestApi()
    api.auth.setup_session(True)
    last_report = 0

    while True:  # take a deep breath

        # use the magic of modulo
        now = datetime.datetime.now()
        report_conditions = (
            now.second,
            now.second % 5 == 0,
            last_report != now.second,
        )
        if not all(report_conditions):
            continue  # this isn’t a report loop

        print("Ping! {0}".format(now))

        last_report = now.second

        for entity_chunk in random.sample(entity_chunks, len(entity_chunks)):

            if entity_chunk.state in (
                EntityChunkState.complete, EntityChunkState.spent
            ): continue  # NOQA

            # how many tasks pending in total
            pending = sum(
                entity_chunk.pending() for entity_chunk in entity_chunks
            )
            if pending <= PROCESSES:  # throttling
                if entity_chunk.state == EntityChunkState.incomplete:
                    entity_chunk.start(pool)

            for entity_page in entity_chunk.entity_pages:
                entity_page.poll()  # updates the state of the EntityPage
                if entity_page.state == EntityPageState.complete:
                    # make cheeky call to populate
                    # populate.main('cache', entity_page.entity_name, metadata)
                    continue
                if entity_page.state == EntityPageState.failed:
                    # handle various failure cases
                    if isinstance(entity_page.exception, EntityPageNoData):
                        # there is no more data, stop requesting this entity
                        entity_chunk.state = EntityChunkState.spent
                        spent_path = os.path.join('cache', 'spent')
                        with open(spent_path, 'rb') as spent_fh:
                            spent = pickle.load(spent_fh)
                            spent.add(entity_chunk.entity_name)
                        with open(spent_path, 'wb') as spent_fh:
                            pickle.dump(spent, spent_fh)
                        LOGGER.info(
                            "{0} ({1}) spent".format(
                                entity_page.entity_name, entity_page.offset
                            )
                        )
                    if isinstance(entity_page.exception, EntityPageDeAuth):
                        api.setup_session(True)
            entity_chunk.poll()  # update state of EntityChunk

        done = (  # ask if all the EntityChunks are done
            (
                entity_chunk.state == EntityChunkState.complete
                or
                entity_chunk.state == EntityChunkState.spent
            )
            for entity_chunk in entity_chunks
        )
        if all(done):
            exit(1)  # move on
        time.sleep(1)  # don’t spam
