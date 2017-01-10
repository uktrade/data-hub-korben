import datetime
import os
import csv
import logging
import tempfile

import sqlalchemy as sqla
from sqlalchemy.dialects.postgresql import insert

from korben import services
from . import download, constants


LOGGER = logging.getLogger('korben.sync.ch.main')
logging.basicConfig(level=logging.DEBUG)

CH_FIELDS = (
    # shared
    'name',
    'company_number',
    'registered_address_1',
    'registered_address_2',
    'registered_address_town',
    'registered_address_county',
    # doesn’t apply, since these are all uk companies?
    # 'registered_address_country',
    'registered_address_postcode',

    # ch only
    'company_category',
    'company_status',
    'sic_code_1',
    'sic_code_2',
    'sic_code_3',
    'sic_code_4',
    'uri',
)

UNITED_KINGDOM_COUNTRY_ID = '80756b9a-5d95-e211-a939-e4115bead28a'


def ch_date(row, column):
    try:
        day, month, year = row[column].split('/')
        return datetime.date(int(year), int(month), int(day))
    except ValueError:
        return None


def csv_chcompany(row):
    ch_company = {}
    for key in CH_FIELDS:
        ch_company[key] = row[key]
    ch_company['incorporation_date'] = ch_date(row, 'incorporation_date')

    # bad hacks
    ch_company['registered_address_country_id'] = UNITED_KINGDOM_COUNTRY_ID
    ch_company['registered_address_3'] = ''
    ch_company['registered_address_4'] = ''

    return ch_company


def insert_or_report(execute_fn, table, rows):
    try:
        execute_fn(insert(table).values(rows))
    except Exception as exc:
        print(rows)
        print(exc)
        return
    LOGGER.info(
        '%s Inserted %s rows',
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        len(rows)
    )


def sync():
    csv_paths = download.extract(download.zips(download.filenames()))
    metadata = services.db.get_django_metadata()
    ch_company_table = metadata.tables['company_companieshousecompany']
    metadata.bind.execute(ch_company_table.delete())
    start_all = datetime.datetime.now()
    chunk_log_fmt = '{0.seconds}.{0.microseconds} for {1} chunk {2}'
    for csv_path in csv_paths:
        LOGGER.info("Starting {0}".format(csv_path))
        start_csv = datetime.datetime.now()
        csv_rows = []
        with open(csv_path, 'r') as csv_fh:
            reader = csv.DictReader(
                csv_fh, fieldnames=constants.SUPPORTED_CSV_FIELDNAMES
            )
            start_chunk = datetime.datetime.now()
            for index, row in enumerate(reader):
                if index == 0:
                    continue  # skip 0th row, since we’re using our own names
                csv_rows.append(csv_chcompany(row))
                if index % 1000 == 0:  # periodically puke rows into the db
                    insert_or_report(
                        metadata.bind.execute, ch_company_table, csv_rows
                    )
                    csv_rows = []
                    LOGGER.debug(chunk_log_fmt.format(
                        datetime.datetime.now() - start_chunk, csv_path, index
                    ))
                    start_chunk = datetime.datetime.now()
            insert_or_report(metadata.bind.execute, ch_company_table, csv_rows)
        LOGGER.info("{0.seconds}.{0.microseconds} for {1}".format(
            datetime.datetime.now() - start_csv, csv_path
        ))
    LOGGER.info("{0.seconds}.{0.microseconds} overall".format(
        datetime.datetime.now() - start_all
    ))

def main():
    one_month = 2629744
    one_day = 86400
    while True:
        if not services.redis.get(constants.CH_FLAG):
            sync()
            services.redis.set(constants.CH_FLAG, '1', ex=one_month)
        time.sleep(one_day)
