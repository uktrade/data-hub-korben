'''
Parse database rows in the form of CSV files from response bodies, throw into
database
'''
import csv
import logging
import os


from korben import config
from korben import services
from . import utils

LOGGER = logging.getLogger('korben.sync.populate')


def resp_csv(cache_dir, csv_dir, col_names, entity_name, page):
    entries = utils.parse_json_entries(cache_dir, entity_name, page)
    if entries is None:
        LOGGER.error("Unpickle of {0} failed on page {1}".format(
            entity_name, page
        ))
        return None, None
    csv_path = os.path.join(csv_dir, page)
    if os.path.isfile(csv_path):
        '''
        print("CSV exists for {0}/{1}, using existing data".format(
            entity_name, page
        ))
        '''
        return None, csv_path
    csv_fh = open(csv_path, 'w')
    writer = csv.DictWriter(csv_fh, col_names, dialect='excel')
    rowcount = 0
    for entry in entries:
        writer.writerow(utils.entry_row(col_names, None, entry))
        rowcount += 1
    csv_fh.close()
    return rowcount, csv_path


def entity_csv(cache_dir, col_names, entity_name, start=0):
    csv_dir = os.path.join(cache_dir, 'csv', entity_name)
    pages = list(
        filter(
            lambda P: int(P) > start,
            sorted(
                os.listdir(os.path.join(cache_dir, 'json', entity_name)),
                key=int,
            )
        )
    )
    LOGGER.info("{0} pages for {1}".format(len(pages), entity_name))
    csv_paths = []
    rowcount = 0
    for page in pages:
        n_rows, csv_path = resp_csv(
            cache_dir, csv_dir, col_names, entity_name, page
        )
        if n_rows and csv_path:
            csv_paths.append(csv_path)
            rowcount += n_rows
        elif csv_path:
            csv_paths.append(csv_path)
            rowcount += 49.9
    LOGGER.info("{0} rows for {1}".format(rowcount, entity_name))
    if len(pages) and not rowcount:
        raise Exception(csv_path)
    return csv_paths


def csv_psql(cursor, csv_path, table):
    LOGGER.info("Using COPY FROM on {0}".format(csv_path))
    with open(csv_path, 'r') as csv_fh:
        cursor.copy_expert(
            '''COPY "{0}" FROM STDIN DELIMITER ',' CSV'''.format(table.name),
            csv_fh
        )
        # cursor.copy_from(csv_fh, '"{0}"'.format(table.name), sep=',', null=None)


def populate_entity(cache_dir, metadata, entity_name):
    os.makedirs(os.path.join(cache_dir, 'csv', entity_name), exist_ok=True)
    table = metadata.tables[entity_name]
    rowcount = metadata.bind.connect().execute(table.count()).scalar()
    col_names = [col.name for col in table.columns]
    csv_paths = entity_csv(cache_dir, col_names, entity_name, rowcount)
    for csv_path in csv_paths:
        try:
            cursor = metadata.bind.connection.cursor()
            csv_psql(cursor, csv_path, table)
        except Exception as exc:
            print("csv_psq call failed for {0} failed".format(csv_path))
            print(exc)


def main(cache_dir='cache', entity_name=None, metadata=None):
    if not metadata:
        metadata = services.db.poll_for_metadata(config.database_odata_url)
    if entity_name:
        populate_entity(cache_dir, metadata, entity_name)
        return
    for entity_name in os.listdir(os.path.join(cache_dir, 'json')):
        populate_entity(cache_dir, metadata, entity_name)
