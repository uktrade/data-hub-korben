import logging

from requests import exceptions as reqs_excs

from . import types
from . import constants
from . import utils

ENTITYPAGE_MODULE_PATH = 'korben.sync.scrape.classes.EntityPage'


class EntityChunk(object):
    '''
    Object to manage the processing of CHUNKSIZE many EntityPage objects, these
    represent a bunch of requests that should be made to fetch data from
    Dynamics. This object basically holds the range and convenience methods for
    reporting on the state of requests in the the chunk.
    '''

    state = types.EntityChunkState.incomplete

    def __init__(self, client, entity_name, offset_start, offset_end):
        self.entity_name = entity_name
        self.offset_start = offset_start
        self.offset_end = offset_end
        self.entity_pages = []
        for offset in range(offset_start, offset_end, constants.PAGESIZE):
            # bung entity pages on to the pile
            self.entity_pages.append(EntityPage(client, entity_name, offset))

    def __str__(self):
        return "<EntityChunk {0} ({1}-{2}) {3}>".format(
            self.entity_name, self.offset_start, self.offset_end, self.state
        )

    def pending(self):
        'Return number of pending tasks'
        return len(list(filter(utils.is_pending, self.entity_pages)))

    def start(self, pool):
        'Start the first "unstarted" task'
        for entity_page in self.entity_pages:
            if entity_page.state == types.EntityPageState.initial:
                entity_page.start(pool)
                break

    def poll(self):
        'Are all the tasks complete?'
        if self.state == types.EntityChunkState.complete:
            return
        entity_page_states = set(
            entity_page.state for entity_page in self.entity_pages
        )
        entity_page_states_initial = (
            state == types.EntityPageState.initial
            for state in entity_page_states
        )
        if all(entity_page_states_initial):
            return
        pending = (
            types.EntityPageState.pending in entity_page_states
            or
            types.EntityPageState.deauthd in entity_page_states
        )
        if not pending:
            if types.EntityPageState.spent in entity_page_states:
                self.state = types.EntityChunkState.spent
            else:
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

    def __init__(self, client, entity_name, offset):
        self.client = client
        self.entity_name = entity_name
        self.offset = offset
        self.logger = logging.getLogger(ENTITYPAGE_MODULE_PATH)

    def __str__(self):
        return "<EntityPage {0} ({1}) {2}>".format(
            self.entity_name, self.offset, self.state
        )

    def reset(self):
        'Used in the case of failure where the request should be made again'
        self.state = types.EntityPageState.initial
        self.task = None
        self.entries = None
        self.rows_inserted = None
        self.exception = None

    def start(self, pool):
        'Send this task to the pool and store the AysyncResult object locally'
        self.task = pool.apply_async(utils.cdms_list, (
            self.client, self.entity_name, self.offset
        ))
        self.state = types.EntityPageState.pending

    def poll(self):
        'Poll self.task, translate exception to state'
        if self.state == types.EntityPageState.initial:
            return  # not started
        if self.state == types.EntityPageState.inserted:
            return  # inserted
        if not self.task.ready():
            return  # pending
        try:
            self.task.get()
            self.state = types.EntityPageState.complete
        except types.EntityPageNoData as exc:
            self.exception = exc
            self.state = types.EntityPageState.spent
        except types.EntityPageDeAuth as exc:
            self.exception = exc
            self.state = types.EntityPageState.deauthd
        except (
            types.EntityPageDynamicsBombed,
            reqs_excs.ConnectionError,
            Exception
        ) as exc:
            self.logger.info(exc)
            self.logger.info("{0} errored, resetting".format(self))
            self.reset()
