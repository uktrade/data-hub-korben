import datetime
import os
import csv
import logging
import tempfile

import sqlalchemy as sqla
from sqlalchemy.dialects.postgresql import insert

from korben import config, db
from . import download, constants


LOGGER = logging.getLogger('korben.sync.ch.main')
logging.basicConfig(level=logging.DEBUG)

CH_FIELDS = (
    'company_number',
    'company_name',
    'registered_address_care_of',
    'registered_address_po_box',
    'registered_address_address_1',
    'registered_address_address_2',
    'registered_address_town',
    'registered_address_county',
    'registered_address_country',
    'registered_address_postcode',
    'company_category',
    'company_status',
    'sic_code_1',
    'sic_code_2',
    'sic_code_3',
    'sic_code_4',
    'uri',
)


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
    return ch_company


def main():
    csv_paths = download.extract(download.zips(download.filenames()))
    metadata = db.poll_for_metadata(config.database_url)
    ch_company_table = metadata.tables['api_chcompany']
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
                if index % 500 == 0:  # periodically puke rows into the db
                    metadata.bind.execute(
                        insert(ch_company_table).values(csv_rows)
                    )
                    csv_rows = []
                    LOGGER.debug(chunk_log_fmt.format(
                        datetime.datetime.now() - start_chunk, csv_path, index
                    ))
                    start_chunk = datetime.datetime.now()
        LOGGER.info("{0.seconds}.{0.microseconds} for {1}".format(
            datetime.datetime.now() - start_csv, csv_path
        ))
    LOGGER.info("{0.seconds}.{0.microseconds} overall".format(
        datetime.datetime.now() - start_all
    ))
