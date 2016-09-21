import datetime
import logging
import multiprocessing
import os
import pickle
import time
import random

from lxml import etree

from korben import config
from korben import etl
from korben import services
from korben.cdms_api.rest.api import CDMSRestApi

from .. import constants
from .. import utils as sync_utils
from . import utils
from . import constants as scrape_constants
from . import types
from . import classes

api = None

class LoggingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('requests')


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('korben.sync.scrape.main')
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


def main(names=None, api_instance=None):
    from korben.etl.main import from_odata_json  # TODO: fix circular dep with sync.utils

    global api
    if api_instance is None:
        api = CDMSRestApi()
        api.auth.setup_session(True)
    else:
        api = api_instance

    pool = multiprocessing.Pool(processes=PROCESSES)
    entity_chunks = []
    spent_path = sync_utils.file_leaf('cache', 'spent')
    metadata = services.db.poll_for_metadata(config.database_odata_url)
    try:
        with open(spent_path, 'rb') as spent_fh:
            spent = pickle.load(spent_fh)
        print("Skipping {0} entity types \o/".format(len(spent)))
    except FileNotFoundError:
        spent = set()
        with open(spent_path, 'wb') as spent_fh:
            pickle.dump(spent, spent_fh)
    if names is None:
        names = set(etl.spec.MAPPINGS.keys())
    else:
        names = set(names.split(','))
    for entity_name in names - spent:
        try:
            caches = sorted(map(int,
                os.listdir(os.path.join('cache', 'json', entity_name))))
            for index, offset in list(enumerate(caches))[1:]:
                if caches[index - 1] != offset - 50:
                    start = caches[index - 1] + 50
                    LOGGER.info(
                        "In a previous run {0} broke at {1}".format(
                            entity_name, start
                        )
                    )
                    break
            else:
                start = max(caches) + 50
        except (FileNotFoundError, ValueError):
            start = 0
        end = start + (scrape_constants.CHUNKSIZE * scrape_constants.PAGESIZE)
        entity_chunks.append(
            classes.EntityChunk(api, entity_name, start, end)
        )
    last_report = 0

    while True:  # take a deep breath

        # use the magic of modulo
        now = datetime.datetime.now()
        report_conditions = (
            now.second,
            now.second % 2 == 0,
            last_report != now.second,
        )
        if not all(report_conditions):
            continue  # this isn’t a report loop

        LOGGER.info("Ping! {0}".format(now.strftime("%Y-%m-%d %H:%M:%S")))

        last_report = now.second

        for entity_chunk in random.sample(entity_chunks, len(entity_chunks)):

            if entity_chunk.state in (
                types.EntityChunkState.complete, types.EntityChunkState.spent
            ):
                LOGGER.info("{0} reports complete".format(entity_chunk))
                continue  # NOQA

            # how many tasks pending in total
            pending = sum(
                entity_chunk.pending() for entity_chunk in entity_chunks
            )
            if pending <= PROCESSES:  # throttling
                if entity_chunk.state == types.EntityChunkState.incomplete:
                    entity_chunk.start(pool)

            for entity_page in entity_chunk.entity_pages:
                entity_page.poll()  # updates the state of the EntityPage
                if entity_page.state == types.EntityPageState.complete:
                    # make cheeky call to etl.load
                    results = from_odata_json(
                        metadata.tables[entity_page.entity_name],
                        utils.json_cache_key(
                            entity_page.entity_name, entity_page.offset
                        )
                    )
                    LOGGER.info(
                        "Records {0}-{1} went into {2}".format(
                            entity_page.offset,
                            entity_page.offset + sum(
                                result.rowcount for result in results
                            ),
                            entity_page.entity_name
                        )
                    )
                    entity_page.state = types.EntityPageState.inserted
                    continue
                if entity_page.state == types.EntityPageState.failed:
                    # handle various failure cases
                    if isinstance(
                            entity_page.exception, types.EntityPageNoData
                    ):
                        # there is no more data, stop requesting this entity
                        entity_chunk.state = types.EntityChunkState.spent
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
                    if isinstance(entity_page.exception, types.EntityPageDeAuth):
                        api.auth.setup_session(True)
            entity_chunk.poll()  # update state of EntityChunk

        done = (  # ask if all the EntityChunks are done
            (
                entity_chunk.state == types.EntityChunkState.complete
                or
                entity_chunk.state == types.EntityChunkState.spent
            )
            for entity_chunk in entity_chunks
        )
        if all(done):
            LOGGER.info('Waiting for Pool.close ...')
            pool.close()
            LOGGER.info('Waiting for Pool.join ...')
            pool.join()
            return  # TODO: add exit(1) somewhere else to signal to bash
        time.sleep(1)  # don’t spam
