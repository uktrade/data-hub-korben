'Unpickle response objects in passed directory, output CSV for loading'
import subprocess
import tempfile
import os
import pickle
import csv
from lxml import etree

from . import constants, utils

PSQL_STRAIGHT = '''
COPY "{0}" FROM '{1}' DELIMITER ',' CSV;
'''

PSQL_DEDUPE = '''
TRUNCATE TABLE "{0}";

CREATE TEMP TABLE "{0}_dedupe" AS SELECT * FROM "{0}" WITH NO DATA;

COPY "{0}_dedupe" FROM '{1}' DELIMITER ',' CSV;

INSERT INTO "{0}" SELECT DISTINCT ON ({2}) * FROM "{0}_dedupe";

DROP TABLE "{0}_dedupe";
'''


def unpickle_resp(resp_dir, entity_name, name):
    path = os.path.join(resp_dir, entity_name, name)
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


def main(metadata, resp_dir, entity_name):
    table = metadata.tables[entity_name + 'Set']
    col_names = [col.name for col in table.columns]
    # assume one column
    primary_key = '"{0}"'.format(
        '","'.join([col.name for col in table.primary_key.columns.values()])
    )
    out_temp = tempfile.NamedTemporaryFile(delete=False)

    out_temp_fh = open(out_temp.name, 'w')
    writer = csv.DictWriter(out_temp_fh, col_names, dialect='excel')
    print("Parsing responses from {0}".format(entity_name))

    pages = sorted(os.listdir(os.path.join(resp_dir, entity_name)), key=int)
    '''
    try:
        sample_entry = unpickle_resp(resp_dir, entity_name, pages[0]).find(ENTRY_TAG)
    except AttributeError:
        print('Could not get sample entry')
        exit(1)
    link_fkey_map = utils.link_fkey_map(table, sample_entry)
    '''
    for page in pages:
        root = unpickle_resp(resp_dir, entity_name, page)
        rows = []
        entries = root.findall(constants.ENTRY_TAG)
        for entry in entries:
            rows.append(utils.entry_row(col_names, None, entry))
        for row in rows:
            writer.writerow(row)
    out_temp_fh.close()
    # print("CSV: {0}".format(out_temp.name))
    # print("SQL: {0}".format(psql_temp.name))
    psql_temp = tempfile.NamedTemporaryFile(delete=False)
    with open(psql_temp.name, 'w') as psql_temp_fh:
        psql_temp_fh.write(
            PSQL_STRAIGHT.format(table.name, out_temp.name)
        )
    psql_proc = subprocess.Popen([
        '/usr/local/pgsql/bin/psql',
        '-d', 'cdms_psql', '-f', psql_temp.name
    ])
    returncode = psql_proc.wait()
    if returncode > 0:
        with open(psql_temp.name, 'w') as psql_temp_fh:
            psql_temp_fh.write(
                PSQL_DEDUPE.format(table.name, out_temp.name, primary_key)
            )
            psql_proc = subprocess.Popen([
                '/usr/local/pgsql/bin/psql',
                '-d', 'cdms_psql', '-f', psql_temp.name
            ])
            returncode = psql_proc.wait()
    return (out_temp, psql_temp), returncode
