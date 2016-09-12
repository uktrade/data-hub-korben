import datetime
import os
import csv
import logging

import sqlalchemy as sqla
from sqlalchemy.dialects.postgresql import insert

from korben import config, db


LOGGER = logging.getLogger('korben.sync.ch')
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
    day, month, year = row[column].split('/')
    return datetime.date(int(year), int(month), int(day))


def csv_chcompany(row):
    ch_company = {}
    for key in CH_FIELDS:
        ch_company[key] = row[key]
    ch_company['incorporation_date'] = ch_date(row, 'incorporation_date')
    return ch_company


def main(filename='/src/korben/test.csv'):
    urls = download.urls()
    metadata = db.poll_for_metadata(config.database_url)
    ch_company_table = metadata.tables['api_chcompany']
    start = datetime.datetime.now()
    with open(filename, 'r') as csv_fh:
        rows = csv.DictReader(csv_fh)
        for row in rows:
            # do upsert
            ch_company = csv_chcompany(row)
            upsert = insert(ch_company_table)\
                .values(**ch_company)\
                .on_conflict_do_update(
                    # this is alternative
                    # constraint='api_chcompany_company_number_59a1c16c_pk',
                    index_elements=['company_number'],
                    set_=ch_company,
                )
            result = connection.execute(upsert)
            LOGGER.debug(result)
    print("{0.seconds}.{0.microseconds}".format(
        datetime.datetime.now() - start
    ))
