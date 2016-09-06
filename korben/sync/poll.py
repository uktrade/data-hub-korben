'''
Do some rough “polling” for entities that have a "ModifiedOn" column, this code
operates under the assumption that there is a fully populated local database.
'''
import datetime
import logging
import multiprocessing
import time

from lxml import etree
import sqlalchemy as sqla

from ..cdms_api.rest.api import CDMSRestApi
from . import constants
from . import utils
from korben import db

CDMS_API = None
ENGINE = None

LOGGER = logging.getLogger('korben.sync.poll')
logging.basicConfig(level=logging.INFO)


def reverse_scrape(entity_name, table, col_names, primary_key, offset):
    connection = ENGINE.connect()
    resp = CDMS_API.list(entity_name, order_by='ModifiedOn desc', skip=offset)
    rows = []
    for entry in etree.fromstring(resp.content).iter(constants.ENTRY_TAG):
        rows.append(utils.entry_row(col_names, None, entry))
    new_rows = 0
    updated_rows = 0
    for row in rows:
        select_statement = (
            sqla
            .select(
                [table.columns[primary_key], table.c.ModifiedOn], table
            )
            .where(
                table.columns[primary_key] == row[primary_key]
            )
        )
        in_db = connection.execute(select_statement).fetchone()
        if in_db:
            try:
                remote_modified = datetime.datetime.strptime(
                    row['ModifiedOn'], "%Y-%m-%d %H:%M:%S"
                )
            except TypeError:
                LOGGER.error("Bad data in {0}".format(entity_name))
                continue
            uuid, local_modified = in_db
            if local_modified < remote_modified:
                update_statement = (
                    table.update()
                         .where(table.columns[primary_key] == row[primary_key])
                         .values(**row)
                )
                result = connection.execute(update_statement)
                assert result.rowcount == 1
                updated_rows += 1
        else:
            result = connection.execute(table.insert().values(**row))
            assert result.rowcount == 1
            new_rows += 1
    LOGGER.info("{2}\n INSERT {0}\n UPDATE {1}".format(
        new_rows, updated_rows, entity_name
    ))
    if new_rows + updated_rows < 50:
        return offset + new_rows + updated_rows
    LOGGER.info(
        "Continuing reverse scrape for {0} (from offset {1})".format(
            entity_name, offset
        )
    )
    connection.close()
    return reverse_scrape(
        entity_name, table, col_names, primary_key, offset + 50
    )

def main():
    global ENGINE
    ENGINE = db.poll_for_engine()
    metadata = sqla.MetaData(bind=ENGINE)
    metadata.reflect()
    global CDMS_API  # NOQA
    CDMS_API = CDMSRestApi()
    with open('korben/odata_psql/entity-table-map/pollable-entities', 'r') as fh:
        pollable_entities = [
            x.strip() for x in fh.readlines()
            if x.strip() not in constants.FORBIDDEN_ENTITIES
        ]
    pool = multiprocessing.Pool()
    results = []
    CDMS_API.auth.setup_session()
    for entity_name in pollable_entities:
        table = metadata.tables[entity_name + 'Set']
        col_names = [x.name for x in table.columns]
        # assume a single column
        primary_key = next(
            col.name for col in table.primary_key.columns.values()
        )
        '''
        LOGGER.info("Starting reverse scrape for {0}".format(entity_name))
        reverse_scrape(entity_name, table, col_names, primary_key, 0)
        '''
        result = pool.apply_async(
            reverse_scrape, (entity_name, table, col_names, primary_key, 0)
        )
        results.append(result)

    pool.close()
    pool.join()
    ENGINE.dispose()
