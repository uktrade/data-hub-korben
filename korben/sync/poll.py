'''
Do some rough “polling” for entities that have a "ModifiedOn" column, this code
operates under the assumption that there is a fully populated local database.
'''
import datetime
import json
import operator
import logging

import sqlalchemy as sqla

from ..cdms_api.rest.api import CDMSRestApi
from .. import etl
from korben import config, services, utils

CDMS_API = None
DATABASE_CONNECTION = None

LOGGER = logging.getLogger('korben.sync.poll')


def get_entry_list(resp):
    resp_json = json.loads(resp.content.decode(resp.encoding or 'utf-8'))
    return resp_json['d']['results']


def reverse_scrape(client,
                   table,
                   against,
                   comparitor,
                   col_names,
                   primary_key,
                   offset):
    resp = client.list(
        table.name, order_by="{0} desc".format(against), skip=offset
    )
    rows = []
    for entry in get_entry_list(resp):
        rows.append(utils.entry_row(col_names, entry))
    new_rows = 0
    updated_rows = 0
    connection = services.db.poll_for_connection(config.database_odata_url)
    for row in rows:
        etl.main.from_odata(table, [row[primary_key]])  # to django
        cols_pkey_against = [
            getattr(table.c, primary_key),
            getattr(table.c, against)
        ]
        select_statement = (
            sqla.select(cols_pkey_against, table)
                .where(table.columns[primary_key] == row[primary_key])
        )
        try:
            pkey, local_against =\
                connection.execute(select_statement).fetchone()
        except TypeError:
            LOGGER.debug('Row in %s doesn’t exist', table.name)
            result = connection.execute(table.insert().values(**row))
            assert result.rowcount == 1
            etl.main.from_odata(table, [row[primary_key]])  # to django
            new_rows += 1
            continue
        LOGGER.debug('local_modified %s', local_against)
        LOGGER.debug('Row in %s exists', table.name)
        try:
            remote_against =\
                datetime.datetime.strptime(row[against], '%Y-%m-%d %H:%M:%S')
        except TypeError:
            LOGGER.error('Bad data in %s', table.name)
            continue
        except ValueError:  # TODO: type introspection (needs lookup object)
            remote_against = row[against]
        if comparitor(local_against, remote_against):
            LOGGER.debug('Row in %s outdated', table.name)
            update_statement = (
                table.update()
                     .where(table.columns[primary_key] == row[primary_key])
                     .values(**row)
            )
            result = connection.execute(update_statement)
            etl.main.from_odata(table, [row[primary_key]])  # to django
            updated_rows += 1
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    LOGGER.info(
        '%s %s INSERT %s UPDATE %s', now, table.name, new_rows, updated_rows
    )
    if new_rows + updated_rows < 50:
        return offset + new_rows + updated_rows
    LOGGER.info(
        'Continuing reverse scrape for %s (from offset %s)', table.name, offset
    )
    return reverse_scrape(
        client, table, against, comparitor, col_names, primary_key, offset + 50
    )


def poll(client=None,
         against='ModifiedOn',
         comparitor=operator.lt,
         entities=None):
    if client is None:
        client = CDMSRestApi()

    odata_metadata = services.db.get_odata_metadata()
    django_metadata = services.db.get_django_metadata()

    live_entities = []
    django_fkey_deps = etl.utils.fkey_deps(django_metadata)
    for depth in sorted(django_fkey_deps.keys()):
        for table_name in django_fkey_deps[depth]:
            if table_name in etl.spec.DJANGO_LOOKUP:
                live_entities.append(etl.spec.DJANGO_LOOKUP[table_name])

    for table_name in entities or live_entities:
        table = odata_metadata.tables[table_name]
        col_names = [x.name for x in table.columns]
        # assume a single column
        primary_key = etl.utils.primary_key(table)
        LOGGER.info('Starting reverse scrape for %s', table.name)
        reverse_scrape(
            client, table, against, comparitor, col_names, primary_key, 0
        )


def main():
    'Poll forever'
    while True:
        poll()
