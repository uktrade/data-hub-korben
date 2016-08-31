import datetime
import multiprocessing
import time
from lxml import etree
import sqlalchemy as sqla
from ..cdms_api.rest.api import CDMSRestApi
from . import resp_csv
from . import constants
from . import utils

def reverse_scrape(cdms_api, entity_name, table, col_names, primary_key, offset):
    start = datetime.datetime.now()
    resp = cdms_api.list(entity_name, order_by='ModifiedOn')
    print("Took {0}s".format((datetime.datetime.now() - start).seconds))
    rows = []
    for entry in etree.fromstring(resp.content).iter(constants.ENTRY_TAG):
        rows.append(utils.entry_row(col_names, None, entry))
    new_rows = 0
    updated_rows = 0
    for row in rows:
        in_db = (
            sqla.select([table.columns[primary_key], table.c.ModifiedOn], table)
                .where(table.columns[primary_key] == row[primary_key])
                .execute()
                .fetchone()
        )
        if in_db:
            remote_modified = datetime.datetime.strptime(
                row['ModifiedOn'], "%Y-%m-%d %H:%M:%S"
            )
            uuid, local_modified = in_db
            if local_modified < remote_modified:
                result = (
                    table.update()
                         .where(table.columns[primary_key] == row[primary_key])
                         .values(**row)
                         .execute()
                )
                assert result.rowcount == 1
                updated_rows += 1
        else:
            table.insert().values(**row)
            new_rows += 1
    print("{0} new and {1} updated".format(new_rows, updated_rows))
    if new_rows + updated_rows < 50:
        return
    print("Continuing reverse scrape for {0}".format(entity_name))
    return reverse_scrape(
        cdms_api, entity_name, table, col_names, primary_key, offset + 50
    )

def main():
    cdms_api = CDMSRestApi()
    engine = sqla.create_engine('postgresql://localhost/cdms_psql')
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    with open('korben/odata_psql/entity-table-map/pollable-entities', 'r') as fh:
        pollable_entities = [
            x.strip() for x in fh.readlines()
            if x.strip() not in constants.FORBIDDEN_ENTITIES
        ]
    pool = multiprocessing.Pool()
    results = []
    for entity_name in pollable_entities:
        table = metadata.tables[entity_name + 'Set']
        col_names = [x.name for x in table.columns]
        # assume a single column
        primary_key = next(col.name for col in table.primary_key.columns.values())
        print("Starting reverse scrape for {0}".format(entity_name))
        reverse_scrape(cdms_api, entity_name, table, col_names, primary_key, 0)
        '''
        result = pool.apply_async(
            reverse_scrape, (cdms_api, entity_name, table, col_names, primary_key, 0)
        )
        results.append(result)
        '''
    '''
    while not all([x.ready() for x in results]):
        time.sleep(1)
    '''
