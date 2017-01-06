import datetime
import logging
import os
import time

import sqlalchemy as sqla

from korben import config


class Singleton(type):
    'Apparently this is a singleton metaclass'
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] =\
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseManager(metaclass=Singleton):
    'Class for managing SQLA metadata objects and database connections'

    connections = {}
    metadatas = {}

    def __init__(self):
        self.logger = logging.getLogger('korben.services.db_manager')

    def reset_connections(self):
        'Close all connections, clear metadata cache'
        for connection in self.connections.values():
            connection.close()
        self.connections = {}
        self.metadatas = {}

    def create_odata_tables(self, connection):
        'Create OData tables against passed connection'
        print('create_odata_tables')
        this_dir = os.path.dirname(__file__)
        create_sql_path = os.path.join(this_dir, 'cdms-psql-create.sql')
        with open(create_sql_path, 'r') as create_sql_fh:
            connection.execute(create_sql_fh.read())

    def get_reflected_metadata(self, connection):
        '''
        Get “reflected-upon” metadata object for passed connection, return a
        tuple of (<how long it took to reflect>, <the metadata object itself>)
        '''
        start = datetime.datetime.now()
        metadata = sqla.MetaData(bind=connection)
        metadata.reflect()
        elapsed = datetime.datetime.now() - start
        return elapsed, metadata

    def poll_for_connection(self, url):
        'Repeatedly attempt to connect to a database at the given URL'
        connection = self.connections.get(url)
        if connection and not connection.closed:
            return connection
        engine = sqla.create_engine(
            url, pool_size=20, max_overflow=0, client_encoding='utf8'
        )
        interval = 1
        while True:
            try:
                connection = engine.connect()
                self.logger.info('Connected to database %s', url)
                break
            except Exception as exc:
                self.logger.error(exc)
                fmt_str = 'Waiting %ss for database %s to come up'
                self.logger.info(fmt_str, interval, url)
                time.sleep(interval)
                interval += 2
        self.connections[url] = connection
        return connection

    def get_odata_metadata(self):
        'Return OData metadata, create tables if they don’t exist'
        metadata = self.metadatas.get('odata')
        if metadata:
            return metadata
        connection = self.poll_for_connection(config.database_odata_url)
        elapsed, metadata = self.get_reflected_metadata(connection)
        if len(metadata.tables) == 0:
            # initial set up case, it’s our responsibility to create tables
            self.logger.info('Creating tables in OData DB')
            self.create_odata_tables(connection)
            elapsed, metadata = self.get_reflected_metadata(connection)
        self.logger.info('Reflection on tables in OData DB took %s', elapsed)
        self.metadatas['odata'] = metadata
        return metadata

    def get_django_metadata(self):
        'Return Django metadata, wait for tables if they don’t exist'
        metadata = self.metadatas.get('django')
        if metadata:
            return metadata
        connection = self.poll_for_connection(config.database_url)
        interval = 1
        while True:
            elapsed, metadata = self.get_reflected_metadata(connection)
            if len(metadata.tables) == 0:
                # initial set up case, before database have tables created.
                # just keep polling
                self.logger.info(
                    'Waiting %ss for tables in Django DB', interval
                )
                time.sleep(interval)
                interval += 2
            else:
                self.logger.info(
                    'Reflection on tables in Django DB took %s', elapsed
                )
                break  # there are some tables there
        self.metadatas['django'] = metadata
        return metadata
