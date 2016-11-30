'''
Do some rough “polling” for entities that have a "ModifiedOn" column, this code
operates under the assumption that there is a fully populated local database.
'''
import datetime
import functools
import json
import operator
import logging

import sqlalchemy as sqla

from ..cdms_api.rest.api import CDMSRestApi
from .. import etl
from korben import config, services, utils
from korben.etl.spec import COLNAME_LONGSHORT, COLNAME_SHORTLONG
from . import leeloo

LOGGER = logging.getLogger('korben.sync.poll')


def get_entry_list(resp):
    'Extract list of entries from response JSON'
    resp_json = json.loads(resp.content.decode(resp.encoding or 'utf-8'))
    # this try except clause is for compatibility with plain OData services
    try:
        return resp_json['d']['results']
    except ValueError:
        return resp_json['d']


class CDMSPoller:
    PAGE_SIZE = 50

    def __init__(self, client=None, against='ModifiedOn', comparator=operator.lt):
        self.client = client or CDMSRestApi()
        self.against = against
        self.comparator = comparator

        self.odata_metadata = services.db.get_odata_metadata()
        self.django_metadata = services.db.get_django_metadata()
        self.conn = services.db.poll_for_connection(config.database_odata_url)

    def pool_entities(self, entities=None):
        entities = entities or self._get_django_tables()

        for table_name in entities:
            table = self.odata_metadata.tables[table_name]
            col_names = [x.name for x in table.columns]

            # assume a single column
            primary_key = etl.utils.primary_key(table)
            LOGGER.info('Starting reverse scrape for %s', table.name)

            self.reverse_scrape(table, col_names, primary_key)

    def reverse_scrape(self, table, col_names, primary_key):
        new_rows = updated_rows = offset = 0

        while new_rows + updated_rows > 0 or offset == 0:
            self.reverse_scrape_page(table, col_names, primary_key, offset)
            offset += self.PAGE_SIZE

            LOGGER.info(
                'Continuing reverse scrape for %s (from offset %s)', table.name, offset
            )

    def reverse_scrape_page(self, table, col_names, primary_key, offset):
        new_rows = 0
        updated_rows = 0

        for row in self._get_rows_to_scrape(table, col_names, offset):
            cols_pkey_against = [
                getattr(table.c, primary_key),
                getattr(table.c, self.against)
            ]
            select_statement = (
                sqla.select(cols_pkey_against, table)
                    .where(table.columns[primary_key] == row[primary_key])
            )

            try:
                _, local_against = self.conn.execute(select_statement).fetchone()
            except TypeError:
                LOGGER.debug('Row in %s doesn’t exist', table.name)
                result = self.conn.execute(table.insert().values(**row))
                assert result.rowcount == 1
                leeloo.send(  # to django
                    *etl.main.from_odata(table, [row[primary_key]], dont_load=True)
                )
                new_rows += 1

                # New row saved, stop here
                continue

            # Existing row, try to update

            LOGGER.debug('local_modified %s', local_against)
            LOGGER.debug('Row in %s exists', table.name)
            # This is quite hacky, since datetime case-handling is hardcoded but
            # optional -- to cover utils.entry_row returning a string and OData
            # test services not having a ModifiedOn type field
            try:
                remote_against = \
                    datetime.datetime.strptime(row[self.against], '%Y-%m-%d %H:%M:%S')
            except TypeError:
                LOGGER.error('Bad data in %s', table.name)
                continue
            except ValueError:  # TODO: type introspection (needs lookup object)
                remote_against = row[self.against]

            if self.comparator(local_against, remote_against) is True:
                LOGGER.debug('Row in %s outdated', table.name)
                update_statement = (
                    table.update()
                         .where(table.columns[primary_key] == row[primary_key])
                         .values(**row)
                )
                self.conn.execute(update_statement)
                leeloo.send(  # to django
                    *etl.main.from_odata(table, [row[primary_key]], dont_load=True)
                )
                updated_rows += 1

            # END LOOP

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        LOGGER.info(
            '%s %s INSERT %s UPDATE %s', now, table.name, new_rows, updated_rows
        )

        return new_rows, updated_rows

    def _get_django_tables(self):
        live_entities = []
        django_fkey_deps = etl.utils.fkey_deps(self.django_metadata)
        for depth in sorted(django_fkey_deps.keys()):
            for table_name in django_fkey_deps[depth]:
                if table_name in etl.spec.DJANGO_LOOKUP:
                    live_entities.append(etl.spec.DJANGO_LOOKUP[table_name])
        return live_entities

    def _get_rows_to_scrape(self, table, col_names, offset):
        resp = self.client.list(
            table.name, order_by="{0} desc".format(self.against), skip=offset
        )
        rows = []

        # ewwww mapping short to long and long to short column names
        short_cols = functools.partial(
            etl.transform.colnames_longshort, table.name
        )
        long_cols = [
            COLNAME_SHORTLONG.get((table.name, short_col), short_col)
            for short_col in col_names
            ]
        for entry in get_entry_list(resp):
            rows.append(short_cols(utils.entry_row(long_cols, entry)))
        # end ewwwww

        return rows


def poll(client=None,
         against='ModifiedOn',
         comparitor=operator.lt,
         entities=None):

    pooler = CDMSPoller(client, against, comparitor)
    pooler.pool_entities(entities)


def main():
    'Poll forever'
    while True:
        pollable_entities = (
            'SystemUserSet',
            'AccountSet',
            'ContactSet',
            'detica_interactionSet',
        )
        poll(entities=pollable_entities)
