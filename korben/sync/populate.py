'Parse database rows in the form of CSV files from XML, throw into database'
import csv
import os
import pickle
import subprocess
from urlparse import urlparse

import sqlalchemy as sqla
from lxml import etree

from korben import config
from . import constants
from . import utils

CSV_PSQL_TEMPLATE = '''
COPY "{0}" FROM '{1}' DELIMITER ',' CSV;
'''


def unpickle_resp(cache_dir, entity_name, name):
    path = os.path.join(cache_dir, 'list', entity_name, name)
    with open(path, 'rb') as resp_fh:
        try:
            resp = pickle.load(resp_fh)
        except:
            print('Bad pickle!')
            # unpickle failed
            return
    try:
        return etree.fromstring(resp.content)
    except etree.XMLSyntaxError:
        print('Bad resp!')
        # scrape failed
        return


def resp_csv(cache_dir, csv_dir, col_names, entity_name, page):
    root = unpickle_resp(cache_dir, entity_name, page)
    if root is None:
        print("Unpickle of {0} failed on page {1}".format(
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
    # print(index + 1, end=' ', flush=True)
    entries = root.findall(constants.ENTRY_TAG)
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
                os.listdir(os.path.join(cache_dir, 'list', entity_name)),
                key=int,
            )
        )
    )
    print("{0} pages for {1}".format(len(pages), entity_name))
    csv_paths = []
    rowcount = 0
    for page in pages:
        n_rows, csv_path = resp_csv(
            cache_dir, csv_dir, col_names, entity_name, page
        )
        if n_rows and csv_path:
            csv_paths.append(csv_path)
            rowcount += n_rows
    print("{0} rows for {1}".format(rowcount, entity_name))
    print("")
    return csv_paths


def csv_psql(cache_dir, csv_path, table):
    psql_path = os.path.join(cache_dir, "{0}.csv".format(table.name))
    with open(psql_path, 'w') as psql_fh:
        psql_fh.write(
            CSV_PSQL_TEMPLATE.format(table.name, os.path.abspath(csv_path))
        )
    url = urlparse(config.database_odata_url)
    return subprocess.check_output([
        'psql',
        '-h', url.netloc,
        '-d', url.path.lstrip('/'),
        '-f', psql_path
    ])


def populate_entity(cache_dir, metadata, entity_name):
    os.makedirs(os.path.join(cache_dir, 'csv', entity_name), exist_ok=True)
    table = metadata.tables[entity_name + 'Set']
    rowcount = metadata.bind.connect().execute(table.count()).scalar()
    '''
    if rowcount and rowcount % 50:
        print(
            '"{0}" appears to be fully populated, skipping'.format(
                table.name
            )
        )
        continue
    '''
    col_names = [col.name for col in table.columns]
    csv_paths = entity_csv(cache_dir, col_names, entity_name, rowcount)
    for csv_path in csv_paths:
        try:
            csv_psql(cache_dir, csv_path, table)
        except subprocess.CalledProcessError:
            print("COPY command for {0} failed".format(csv_path))


def main(cache_dir='cache', entity_name=None, metadata=None):
    if not metadata:
        engine = sqla.create_engine(config.database_odata_url)
        metadata = sqla.MetaData(bind=engine)
        metadata.reflect()
    if entity_name:
        populate_entity(cache_dir, metadata, entity_name)
        return
    for entity_name in os.listdir(os.path.join(cache_dir, 'list')):
        populate_entity(cache_dir, metadata, entity_name)
