'''
Do some rough “polling” for entities that have a "ModifiedOn" column, this code
operates under the assumption that there is a fully populated local database.
'''
import datetime
import functools
import json
import logging
import operator
import os
import time

import sqlalchemy as sqla

from korben import config, services, utils
from korben.bau.sentry_client import SENTRY_CLIENT
from korben.etl.spec import COLNAME_SHORTLONG

from . import leeloo
from .. import etl
from ..cdms_api.rest.api import CDMSRestApi

LOGGER = logging.getLogger('korben.sync.poll')
HEARTBEAT = 'cdms-polling-heartbeat'
HEARTBEAT_FREQ = 900
POLL_SLEEP = int(os.environ.get('KORBEN_POLL_SLEEP', 5))


def get_entry_list(resp):
    'Extract list of entries from response JSON'
    resp_json = json.loads(resp.content.decode(resp.encoding or 'utf-8'))
    # this try except clause is for compatibility with plain OData services
    try:
        return resp_json['d']['results']
    except TypeError:
        return resp_json['d']


class CDMSPoller:
    'Class to poll for updates from CDMS'
    PAGE_SIZE = 50

    def __init__(self,
                 client=None,
                 against='ModifiedOn',
                 comparator=operator.lt):
        'Arguments are optional here to allow for testing against OData'
        self.client = client or CDMSRestApi()
        self.against = against
        self.comparator = comparator

        self.odata_metadata = services.db.get_odata_metadata()
        self.django_metadata = services.db.get_django_metadata()
        self.db = services.db.poll_for_connection(config.database_odata_url)

    def poll_entities(self, entities=None):
        'Poll for a set of entities, if no entities are passed all are polled'
        entities = entities or self._entities_dep_order()

        for table_name in entities:
            table = self.odata_metadata.tables[table_name]
            col_names = [x.name for x in table.columns]

            # assume a single column
            primary_key = etl.utils.primary_key(table)
            LOGGER.debug('Starting reverse scrape for %s', table.name)

            self.reverse_scrape(table, col_names, primary_key)
            services.redis.set(HEARTBEAT, 'bumbum', ex=HEARTBEAT_FREQ)
            time.sleep(POLL_SLEEP)

    def reverse_scrape(self, table, col_names, primary_key):
        '''
        Main polling logic:

        Download pages of PAGE_SIZE entries by increasing offset until less
        than PAGE_SIZE combined updates and inserts happen, which is taken as
        indication that that entity doesn’t have any more changes.
        '''
        updates = offset = 0

        while not updates < self.PAGE_SIZE or offset == 0:
            updates = self.reverse_scrape_page(
                table, col_names, primary_key, offset
            )
            offset += self.PAGE_SIZE

            LOGGER.debug(
                'Continuing reverse scrape for %s (from offset %s)',
                table.name, offset
            )

    def _insert(self, table, primary_key, row):
        result = self.db.execute(table.insert().values(**row))
        leeloo.send(
            *etl.main.from_odata(table, [row[primary_key]], dont_load=True)
        )
        return result.rowcount

    def _local_against(self, table, primary_key, row):
        cols_pkey_against = [
            getattr(table.c, primary_key),
            getattr(table.c, self.against)
        ]
        select_statement = (
            sqla.select(cols_pkey_against, table)
                .where(table.columns[primary_key] == row[primary_key])
        )
        _, local_against = self.db.execute(select_statement).fetchone()
        return local_against

    def _update(self, table, primary_key, row):
        update_statement = (
            table.update()
                 .where(table.columns[primary_key] == row[primary_key])
                 .values(**row)
        )
        result = self.db.execute(update_statement)
        leeloo.send(  # to django
            *etl.main.from_odata(table, [row[primary_key]], dont_load=True)
        )
        return result.rowcount

    def reverse_scrape_page(self, table, col_names, primary_key, offset):
        '''
        Download a single page of entries for the given entity type, tee'ing
        data to the local storage and Leeloo, returning the sum of new and
        updated rows that resulted.
        '''
        new_rows = updated_rows = 0

        for row in self._get_rows_to_scrape(table, col_names, offset):
            try:
                local_against = self._local_against(table, primary_key, row)
            except TypeError:
                LOGGER.debug('Row in %s doesn’t exist', table.name)
                new_rows += self._insert(table, primary_key, row)
                continue  # New row saved, stop here

            # Existing row, try to update

            LOGGER.debug('Row in %s exists', table.name)
            LOGGER.debug('Local against value is %s', local_against)
            # This is quite hacky, since datetime case-handling is hardcoded
            # but optional -- to cover utils.entry_row returning a string and
            # OData test services not having a ModifiedOn type field
            try:
                remote_against = datetime.datetime.strptime(
                    row[self.against], '%Y-%m-%d %H:%M:%S'
                )
            except TypeError:
                LOGGER.error('Bad data in %s', table.name)
                continue
            except ValueError:  # TODO: type introspection (needs lookup
                                # object)
                remote_against = row[self.against]

            if self.comparator(local_against, remote_against) is True:
                LOGGER.debug('Row in %s outdated', table.name)
                updated_rows += self._update(table, primary_key, row)

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        LOGGER.debug(
            '%s %s INSERT %s UPDATE %s',
            now, table.name, new_rows, updated_rows
        )

        return new_rows + updated_rows

    def _get_rows_to_scrape(self, table, col_names, offset):
        '''
        Make a single request according to ordering parameter, transform from
        OData JSON format to OData database row format.

        See https://github.com/uktrade/data-hub-odata-psql for the full dope.
        '''
        try:
            resp = self.client.list(
                table.name,
                order_by="{0} desc".format(self.against),
                skip=offset,
                top=self.PAGE_SIZE,
            )
        except Exception as exc:
            SENTRY_CLIENT.captureException()
            raise exc
        LOGGER.info(
            '%s offset %s took %s seconds',
            table.name, offset, resp.elapsed.seconds
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

    def _entities_dep_order(self):
        '''
        Directly access Leeloo’s schema and return OData names in schema
        dependency order
        '''
        live_entities = []
        django_fkey_deps = etl.utils.fkey_deps(self.django_metadata)
        for depth in sorted(django_fkey_deps.keys()):
            for table_name in django_fkey_deps[depth]:
                if table_name in etl.spec.DJANGO_LOOKUP:
                    live_entities.append(etl.spec.DJANGO_LOOKUP[table_name])
        return live_entities


def main():
    'Poll forever'
    while True:
        pollable_entities = (
            'SystemUserSet',
            'AccountSet',
            'ContactSet',
            'detica_interactionSet',
        )
        poller = CDMSPoller()
        poller.poll_entities(pollable_entities)
