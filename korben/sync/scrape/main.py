import datetime
import logging
import multiprocessing
import os
import pickle
import time
import random

from korben import etl
from korben import services
from korben.cdms_api.rest.api import CDMSRestApi

from .. import utils as sync_utils
from . import utils
from . import constants as scrape_constants
from . import types
from . import classes


class LoggingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('requests')


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('korben.sync.scrape.main')
logging.getLogger().addFilter(LoggingFilter())

SPENT_PATH = sync_utils.file_leaf('cache', 'spent')


def main(names=None, client=None):
    if not client:  # assume this is not a testing case
        # force login to setup cookie to be used by subsequent client instances
        CDMSRestApi().auth.setup_session(True)
    if names is None:
        names = etl.spec.MAPPINGS.keys()
    else:
        names = set(names.split(','))
    pool = multiprocessing.Pool(processes=scrape_constants.PROCESSES)
    entity_chunks = []
    metadata = services.db.get_odata_metadata()
    try:
        with open(SPENT_PATH, 'rb') as spent_fh:
            spent = pickle.load(spent_fh)
        print("Skipping {0} entity types \o/".format(len(spent)))
    except FileNotFoundError:
        spent = set()
        with open(SPENT_PATH, 'wb') as spent_fh:
            pickle.dump(spent, spent_fh)
    to_scrape = names - spent
    LOGGER.info('Scraping the following entities:')
    for name in names:
        LOGGER.info('    %s %s', name, '✔' if name in to_scrape else '✘')
    for entity_name in to_scrape:
        try:
            # validate cache is in good shape (ie. no missing requests)
            cache_names = os.listdir(
                os.path.join('cache', 'json', entity_name)
            )
            caches = sorted(map(int, cache_names))
            for index, offset in list(enumerate(caches))[1:]:
                if caches[index - 1] != offset - 50:
                    start = caches[index - 1] + 50
                    LOGGER.info(
                        'In a previous run %s broke at %s', entity_name, start
                    )
                    break
            else:
                start = max(caches) + 50
        except (FileNotFoundError, ValueError):
            start = 0
        end = start + (scrape_constants.CHUNKSIZE * scrape_constants.PAGESIZE)
        entity_chunks.append(
            classes.EntityChunk(client, entity_name, start, end)
        )
    last_report = 0

    while True:  # take a deep breath

        # use the magic of modulo
        now = datetime.datetime.now()
        report_conditions = (
            now.second,
            now.second % scrape_constants.INTERVAL == 0,
            last_report != now.second,
        )
        if not all(report_conditions):
            continue  # this isn’t a report loop

        LOGGER.info("{0}".format(now.strftime("%Y-%m-%d %H:%M:%S")))

        last_report = now.second
        reauthd_this_tick = False

        for entity_chunk in random.sample(entity_chunks, len(entity_chunks)):

            if entity_chunk.state in (
                types.EntityChunkState.complete, types.EntityChunkState.spent
            ):
                # LOGGER.info("{0} reports complete".format(entity_chunk))
                continue  # NOQA

            # how many tasks pending in total
            pending = sum(
                entity_chunk.pending() for entity_chunk in entity_chunks
            )
            if pending <= scrape_constants.PROCESSES:  # throttling
                if entity_chunk.state == types.EntityChunkState.incomplete:
                    entity_chunk.start(pool)

            for entity_page in entity_chunk.entity_pages:
                entity_page.poll()  # updates the state of the EntityPage
                if entity_page.state == types.EntityPageState.complete:
                    # make cheeky call to etl.load
                    results, _ = etl.main.from_odata_json(
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
                if entity_page.state == types.EntityPageState.spent:
                    # there is no more data, stop requesting this entity
                    entity_chunk.state = types.EntityChunkState.spent
                    with open(SPENT_PATH, 'rb') as spent_fh:
                        spent = pickle.load(spent_fh)
                        spent.add(entity_chunk.entity_name)
                    with open(SPENT_PATH, 'wb') as spent_fh:
                        pickle.dump(spent, spent_fh)
                    LOGGER.error(
                        "{0} ({1}) spent".format(
                            entity_page.entity_name, entity_page.offset
                        )
                    )
                if entity_page.state == types.EntityPageState.deauthd:
                    if not reauthd_this_tick:
                        CDMSRestApi().auth.setup_session(True)
                        reauthd_this_tick = True
                    entity_page.reset()
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
            if not client:  # assume this is not a testing case
                exit(1)
            return
        time.sleep(1)  # don’t spam
