'''
Do some rough “polling” for entities that have a "ModifiedOn" column, this code
operates under the assumption that there is a fully populated local database.
'''
import datetime
import logging
import multiprocessing

from lxml import etree
import sqlalchemy as sqla

from ..cdms_api.rest.api import CDMSRestApi
from ..etl.main import from_cdms_psql
from .. import etl
from . import constants
from . import utils
from korben import config, services

CDMS_API = None
DATABASE_CONNECTION = None

LOGGER = logging.getLogger('korben.sync.poll')
LOGGER.addHandler(utils.MultiProcessingLog)


def reverse_scrape(table, col_names, primary_key, offset):
    resp = CDMS_API.list(table.name, order_by='ModifiedOn desc', skip=offset)
    rows = []
    for entry in etree.fromstring(resp.content).iter(constants.ENTRY_TAG):
        rows.append(utils.entry_row(col_names, None, entry))
    new_rows = 0
    updated_rows = 0
    connection = services.db.poll_for_connection(config.database_odata_url)
    for row in rows:
        from_cdms_psql(table, [row[primary_key]])
        select_statement = (
            sqla.select([table.c.ModifiedOn], table)
                .where(table.columns[primary_key] == row[primary_key])
        )
        local_modified = connection.execute(select_statement).scalar()
        LOGGER.debug("local_modified {0}".format(local_modified))
        if local_modified:
            LOGGER.debug("row in {0} exists".format(table.name))
            try:
                remote_modified = datetime.datetime.strptime(
                    row['ModifiedOn'], "%Y-%m-%d %H:%M:%S"
                )
            except TypeError:
                LOGGER.error("Bad data in {0}".format(table.name))
                continue
            if local_modified < remote_modified:
                LOGGER.debug("row in {0} outdated".format(table.name))
                update_statement = (
                    table.update()
                         .where(table.columns[primary_key] == row[primary_key])
                         .values(**row)
                )
                result = connection.execute(update_statement)
                from_cdms_psql(table, [row[primary_key]])
                updated_rows += 1
        else:
            LOGGER.debug("row in {0} doesn't exist".format(table.name))
            result = connection.execute(table.insert().values(**row))
            assert result.rowcount == 1
            from_cdms_psql(table, [row[primary_key]])
            new_rows += 1
    LOGGER.info("{3} {2} INSERT {0} UPDATE {1}".format(
        new_rows, updated_rows, table.name, datetime.datetime.now()
    ))
    if new_rows + updated_rows < 50:
        return offset + new_rows + updated_rows
    LOGGER.info("Continuing reverse scrape for {0} (from offset {1})".format(
        table.name, offset
    ))
    return reverse_scrape(table, col_names, primary_key, offset + 50)


def poll_():
    global CDMS_API  # NOQA
    CDMS_API = CDMSRestApi()

    odata_metadata = services.db.poll_for_metadata(config.database_odata_url)
    django_metadata = services.db.poll_for_metadata(config.database_url)

    pool = multiprocessing.Pool()
    results = []

    live_entities = []
    django_fkey_deps = etl.utils.fkey_deps(django_metadata)
    for depth in sorted(django_fkey_deps.keys()):
        for table_name in django_fkey_deps[depth]:
            if table_name in etl.spec.DJANGO_LOOKUP:
                live_entities.append(etl.spec.DJANGO_LOOKUP[table_name])

    CDMS_API.auth.setup_session()

    for table_name in live_entities:
        table = odata_metadata.tables[table_name]
        col_names = [x.name for x in table.columns]
        # assume a single column
        primary_key = next(
            col.name for col in table.primary_key.columns.values()
        )
        '''
        LOGGER.info("Starting reverse scrape for {0}".format(table.name))
        reverse_scrape(table, col_names, primary_key, 0)
        '''
        result = pool.apply_async(
            reverse_scrape, (table, col_names, primary_key, 0)
        )
        results.append(result)

    pool.close()
    pool.join()


def main():
    'Poll forever'
    while True:
        poll_()
