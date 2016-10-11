import datetime
import logging
import os
import time

import sqlalchemy as sqla

from korben import config

LOGGER = logging.getLogger('korben.services.db')

__ODATA_METADATA__ = None
__DJANGO_METADATA__ = None

__CONNECTIONS__ = {}


def disconnect_all():
    'Try and drop connections'
    global __DJANGO_METADATA__
    if __DJANGO_METADATA__ is not None:
        __DJANGO_METADATA__.bind.close()
    global __ODATA_METADATA__
    if __ODATA_METADATA__ is not None:
        __ODATA_METADATA__.bind.close()
    __DJANGO_METADATA__ = None
    __ODATA_METADATA__ = None


def create_tables(connection):
    'Create CDMS tables against passed connection'
    this_dir = os.path.dirname(__file__)
    create_sql_path = os.path.join(this_dir, 'cdms-psql-create.sql')
    with open(create_sql_path, 'r') as create_sql_fh:
        connection.execute(create_sql_fh.read())


def get_reflected_metadata(connection):
    '''
    Get “reflected-upon” metadata object for passed connection, return a tuple
    of (<how long it took to reflect>, <the metadata object itself>)
    '''
    start = datetime.datetime.now()
    metadata = sqla.MetaData(bind=connection)
    metadata.reflect()
    elapsed = datetime.datetime.now() - start
    return elapsed, metadata


def poll_for_connection(url):
    'Repeatedly attempt to connect to a database at the given URL'
    global __CONNECTIONS__
    connection = __CONNECTIONS__.get(url)
    if connection:
        return connection
    engine = sqla.create_engine(
        url, pool_size=20, max_overflow=0, client_encoding='utf8'
    )
    interval = 1
    while True:
        try:
            connection = engine.connect()
            LOGGER.info('Connected to database %s', url)
            break
        except Exception as exc:
            LOGGER.error(exc)
            fmt_str = 'Waiting %ss for database %s to come up'
            LOGGER.info(fmt_str, interval, url)
            time.sleep(interval)
            interval += 2
    __CONNECTIONS__[url] = connection
    return connection


def get_odata_metadata():
    'Return OData metadata, create tables if they don’t exist'
    global __ODATA_METADATA__
    if __ODATA_METADATA__ is not None:
        return __ODATA_METADATA__
    connection = poll_for_connection(config.database_odata_url)
    elapsed, metadata = get_reflected_metadata(connection)
    if len(metadata.tables) == 0:
        # initial set up case, it’s our responsibility to create tables
        LOGGER.info('Creating tables in OData DB')
        create_tables(connection)
        elapsed, metadata = get_reflected_metadata(connection)
    LOGGER.info('Reflection on tables in OData DB took %s', elapsed)
    __ODATA_METADATA__ = metadata
    return metadata


def get_django_metadata():
    'Return Django metadata, wait for tables if they don’t exist'
    global __DJANGO_METADATA__
    if __DJANGO_METADATA__ is not None:
        return __DJANGO_METADATA__
    connection = poll_for_connection(config.database_url)
    interval = 1
    while True:
        elapsed, metadata = get_reflected_metadata(connection)
        if len(metadata.tables) == 0:
            # initial set up case, before database have tables created.
            # just keep polling
            LOGGER.info('Waiting %ss for tables in Django DB', interval)
            time.sleep(interval)
            interval += 2
        else:
            LOGGER.info('Reflection on tables in Django DB took %s', elapsed)
            break  # there are some tables there
    __DJANGO_METADATA__ = metadata
    return metadata
