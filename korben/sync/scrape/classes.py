import datetime
import logging
import os
import pickle

from requests import exceptions as reqs_excs

from korben.cdms_api.rest.api import CDMSRestApi
from . import types
from . import constants
from . import utils

LOGGER = logging.getLogger('korben.sync.scrape.classes')

api = CDMSRestApi()

def request_cache_key(entity_name, offset):
    'Return the path where a request cache entry should be written'
    return utils.file_leaf('cache', 'request', entity_name, offset)


def duration_record(entity_name, offset):
    'Return the path where a request duration record should be written'
    return utils.file_leaf('cache', 'duration', entity_name, offset)


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


def is_pending(entity_page):
    'Convenience function to test if an EntityPage object is in pending state'
    return entity_page.state == types.EntityPageState.pending


def cdms_list(entity_name, offset):
    '''
    Call the `cdms_api.list` method, passing through the entity_name and
    offset. This function records the duration of the network request. It also
    caches the resulting response if it’s successful and raises an informative
    exception if it’s not.
    '''
    cached, cache_path = is_cached(entity_name, offset)
    if cached:  # nothing to do, just load resp from cache
        with open(cache_path, 'rb') as cache_fh:
            return pickle.load(cache_fh)
    start_time = datetime.datetime.now()
    resp = api.list(entity_name, skip=offset)  # the actual request
    time_delta = (datetime.datetime.now() - start_time).seconds

    # the below will raise if the response is no good
    utils.raise_on_cdms_resp_errors(entity_name, offset, resp)

    # record our expensive network request
    with open(duration_record(entity_name, offset), 'w') as duration_fh:
        duration_fh.write(str(time_delta))
    with open(cache_path, 'wb') as cache_fh:
        pickle.dump(resp, cache_fh)
    LOGGER.info("{0} ({1}) {2}s".format(entity_name, offset, time_delta))
    return resp


class EntityChunk(object):
    '''
    Object to manage the processing of CHUNKSIZE many EntityPage objects, these
    represent a bunch of requests that should be made to fetch data from
    Dynamics. This object basically holds the range and convenience methods for
    reporting on the state of requests.
    '''

    state = types.EntityChunkState.incomplete

    def __init__(self, entity_name, offset_start, offset_end):
        self.entity_name = entity_name
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.entity_pages = []
        for offset in range(offset_start, offset_end, constants.PAGESIZE):
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
            if entity_page.state == types.EntityPageState.initial:
                entity_page.start(pool)
                break

    def poll(self):
        'Are all the tasks complete?'
        done = (
            entity_page.state == types.EntityPageState.complete
            for entity_page in self.entity_pages
        )
        if all(done):
            self.state = types.EntityChunkState.complete


class EntityPage(object):
    '''
    Object representing a single request to Dyanmics. Knows how to map from a
    bunch of different exceptions to state that can be examined higher up the
    call graph.
    '''

    state = types.EntityPageState.initial
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
        self.state = types.EntityPageState.initial
        self.task = None
        self.entries = None
        self.rows_inserted = None
        self.exception = None

    def start(self, pool):
        'Send this task to the pool and store the AysyncResult object locally'
        self.task = pool.apply_async(cdms_list, (
            self.entity_name, self.offset
        ))
        self.state = types.EntityPageState.pending

    def poll(self):
        'Poll self.task, translate exception to state'
        if self.state == types.EntityPageState.initial:
            return  # not started
        if not self.task.ready():
            return  # pending
        try:
            self.task.get()
            self.state = types.EntityPageState.complete
        except (types.EntityPageNoData, types.EntityPageDeAuth) as exc:
            self.exception = exc
            self.state = types.EntityPageState.failed
        except (
            types.EntityPageDynamicsBombed,
            reqs_excs.ConnectionError,
            RuntimeError
        ) as exc:
            LOGGER.debug(exc)
            LOGGER.error("{0} errored, resetting".format(self))
            self.reset()
