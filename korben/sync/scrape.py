import datetime
import enum
import logging
import multiprocessing
import os
import pickle
import time
import random
import uuid

from korben.cdms_api.connection import rest_connection as api

from lxml import etree

from . import constants

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger('korben.sync.scrape')

try:
    with open('popular-entities', 'r') as entity_names_fh:
        ENTITY_NAMES = [name.strip() for name in entity_names_fh.readlines()]
    print('Using popular-entities file:')
    for entity_name in ENTITY_NAMES:
        print("  {0}".format(entity_name))
except FileNotFoundError:
    ENTITY_NAMES = constants.ENTITY_NAMES

PROCESSES = 128
CHUNKSIZE = 5000


def file_leaf(*args):
    path = os.path.join(*map(str, args))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def list_cache_key(entity_name, offset):
    return file_leaf('cache', 'list', entity_name, offset)


def timing_record(entity_name, offset):
    return file_leaf('cache', 'timing', entity_name, offset)

def is_cached(entity_name, offset):
    path = list_cache_key(entity_name, offset)
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
    cached, cache_path = is_cached(entity_name, offset)
    if cached:
        with open(cache_path, 'rb') as cache_fh:
            return pickle.load(cache_fh)
    start_time = datetime.datetime.now()
    resp = api.list(entity_name, skip=offset)
    time_delta = (datetime.datetime.now() - start_time).seconds
    if not resp.ok:
        try:
            root = etree.fromstring(resp.content)
            if 'paging' in root.find(constants.MESSAGE_TAG).text:
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
    try:
        root = etree.fromstring(resp.content)  # check XML is parseable
        if not root.findall('{http://www.w3.org/2005/Atom}entry'):
            # paged out in a useless way
            raise EntityPageNoData(
                "{0} {1}".format(entity_name, offset)
            )
    except etree.XMLSyntaxError as exc:
        raise EntityPageDeAuth(
            "{0} {1}".format(entity_name, offset)
        )
    # record our expensive network request
    with open(timing_record(entity_name, offset), 'w') as timing_fh:
        timing_fh.write(str(time_delta))
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
#               |
#               |
            'pending',
#             /   \
#            /     \
       'failed', 'complete',
    )
)

EntityChunkState = enum.Enum(
    'EntityChunkState',
    (
           'incomplete',
#             /   \
#            /     \
        'spent', 'complete',
    )
)

is_pending = lambda entity_page: entity_page.state == EntityPageState.pending

class EntityChunk(object):

    state = EntityChunkState.incomplete

    def __init__(self, entity_name, offset_start, offset_end):
        self.entity_name = entity_name
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.entity_pages = []
        for offset in range(offset_start, offset_end, 50):
            self.entity_pages.append(EntityPage(entity_name, offset))

    def __str__(self):
        return "<EntityChunk {0} ({1}-{2})>".format(
            self.entity_name, self.offset_start, self.offset_end
        )


    def pending(self):
        'Return number of pending tasks'
        return len(list(filter(is_pending, self.entity_pages)))

    def start(self, pool):
        'Start the first "unstarted" EntityPage'
        for entity_page in self.entity_pages:
            if entity_page.state == EntityPageState.initial:
                entity_page.start(pool)
                break

    def done(self):
        'Are all the tasks complete'
        done = (
            entity_page.state == EntityPageState.complete
            for entity_page in self.entity_pages
        )
        if all(done):
            self.state = EntityChunkState.complete



class EntityPage(object):

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
        self.state = EntityPageState.initial
        self.task = None
        self.entries = None
        self.rows_inserted = None
        self.exception = None


    def start(self, pool):
        self.task = pool.apply_async(cdms_list, (
            self.entity_name, self.offset
        ))
        self.state = EntityPageState.pending

    def poll(self):
        if self.state == EntityPageState.initial:
            return  # not started
        if not self.task.ready():
            return  # pending
        try:
            result = self.task.get()
            self.state = EntityPageState.complete
        except (EntityPageNoData, EntityPageDeAuth) as exc:
            self.exception = exc
            self.state = EntityPageState.failed
        except EntityPageDynamicsBombed:
            self.reset()


def main():
    pool = multiprocessing.Pool(processes=PROCESSES)
    entity_chunks = []
    spent_path = os.path.join('cache', 'spent')
    try:
        with open(spent_path, 'rb') as spent_fh:
            spent = pickle.load(spent_fh)
    except FileNotFoundError:
        spent = set()
        with open(spent_path, 'wb') as spent_fh:
            pickle.dump(spent, spent_fh)
    print("The follow entities are spent, skipping:")
    for entity_name in spent:
        print("  {0}".format(entity_name))
    for entity_name in set(constants.ENTITY_NAMES) - spent:
        try:
            caches = os.listdir(os.path.join('cache', 'list', entity_name))
            start = max(map(int, caches)) + 50
        except (FileNotFoundError, ValueError) as exc:
            start = 0
        end = start + CHUNKSIZE
        entity_chunks.append(EntityChunk(entity_name, start, end))

    api.auth.setup_session(True)
    last_report = 0

    while True:  # take a deep breath

        now = datetime.datetime.now()
        report_conditions = (
            now.second,
            now.second % 5 == 0,
            last_report != now.second,
        )
        if not all(report_conditions):
            continue  # this isn’t a report loop

        last_report = now.second

        for entity_chunk in random.sample(entity_chunks, len(entity_chunks)):
            pending = sum(
                entity_chunk.pending() for entity_chunk in entity_chunks
            )

            # throttling
            if pending <= PROCESSES:
                if entity_chunk.state == EntityChunkState.incomplete:
                    entity_chunk.start(pool)

            for entity_page in entity_chunk.entity_pages:
                entity_page.poll()
                if entity_page.state == EntityPageState.complete:
                    continue
                if entity_page.state == EntityPageState.failed:
                    if isinstance(entity_page.exception, EntityPageNoData):
                        entity_chunk.state = EntityChunkState.spent
                        with open(os.path.join('cache', 'spent'), 'rb') as spent_fh:
                            spent = pickle.load(spent_fh)
                            spent.add(entity_chunk.entity_name)
                        with open(os.path.join('cache', 'spent'), 'wb') as spent_fh:
                            pickle.dump(spent, spent_fh)
                    if isinstance(entity_page.exception, EntityPageDeAuth):
                        api.setup_sesstion(True)
            entity_chunk.done()  # do a bit of polling

        done = (
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
