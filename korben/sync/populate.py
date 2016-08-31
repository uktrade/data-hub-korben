'Parse database rows in the form of CSV files from XML, throw into database'
import csv
import os
import pickle
import subprocess

import sqlalchemy as sqla
from lxml import etree

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


def entity_csv(cache_dir, col_names, entity_name):
    csv_dir = os.path.join(cache_dir, 'csv', entity_name)
    pages = sorted(
        os.listdir(os.path.join(cache_dir, 'list', entity_name)),
        key=int,
    )
    print("{0} pages for {1}".format(len(pages), entity_name))
    csv_paths = []
    rowcount = 0
    for index, page in enumerate(pages):
        root = unpickle_resp(cache_dir, entity_name, page)
        if root is None:
            print("Unpickle of {0} failed on page {1}".format(
                entity_name, page
            ))
            continue
        csv_path = os.path.join(csv_dir, page)
        if os.path.isfile(csv_path):
            print("CSV exists for {0}/{1}, using existing data".format(
                entity_name, page
            ))
            continue
        csv_fh = open(csv_path, 'w')
        writer = csv.DictWriter(csv_fh, col_names, dialect='excel')
        # print(index + 1, end=' ', flush=True)
        entries = root.findall(constants.ENTRY_TAG)
        for entry in entries:
            writer.writerow(utils.entry_row(col_names, None, entry))
            rowcount += 1
        csv_fh.close()
        csv_paths.append(csv_path)
    print("{0} rows for {1}".format(rowcount, entity_name))
    print("")
    return csv_paths


def csv_psql(cache_dir, csv_path, table):
    psql_path = os.path.join(cache_dir, "{0}.csv".format(table.name))
    with open(psql_path, 'w') as psql_fh:
        psql_fh.write(
            CSV_PSQL_TEMPLATE.format(table.name, os.path.abspath(csv_path))
        )
    return subprocess.check_output([
        'psql', '-d', 'cdms_psql', '-f', psql_path
    ])


def main(cache_dir='cache'):
    engine = sqla.create_engine('postgresql://localhost/cdms_psql')
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    connection = engine.connect()
    for entity_name in os.listdir(os.path.join(cache_dir, 'list')):
        os.makedirs(
            os.path.join(cache_dir, 'csv', entity_name), exist_ok=True
        )
        table = metadata.tables[entity_name + 'Set']
        if connection.execute(table.count()).scalar():
            print(
                '"{0}" appears already to be populated, skipping'.format(
                    table.name
                )
            )
            continue
        col_names = [col.name for col in table.columns]
        csv_paths = entity_csv(cache_dir, col_names, entity_name)
        for csv_path in csv_paths:
            try:
                csv_psql(cache_dir, csv_path, table)
            except subprocess.CalledProcessError:
                print("COPY command for {0} failed".format(csv_path))
