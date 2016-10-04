import datetime
import logging
import time
import sqlalchemy as sqla

from korben import config

LOGGER = logging.getLogger('korben.services.db')

__CACHE__ = {}


def poll_for_metadata(url):
    metadata = __CACHE__.get("{0}-{1}".format('metadata', url), None)
    if metadata is None:
        connection = __CACHE__.get("{0}-{1}".format('connection', url), None)
        if connection is None:
            connection = poll_for_connection(url)
        interval = 1
        while True:
            start = datetime.datetime.now()
            metadata = sqla.MetaData(bind=connection)
            metadata.reflect()
            elapsed = datetime.datetime.now() - start
            if len(metadata.tables) == 0:
                # initial set up case, before database have tables created.
                # just keep polling
                LOGGER.info('Waiting %ss for tables in db %s', interval, url)
                time.sleep(interval)
                interval += 2
            else:
                LOGGER.info('Reflected on tables in %s over %s', url, elapsed)
                break  # there are some tables there
        __CACHE__["{0}-{1}".format('metadata', url)] = metadata
    return metadata


def poll_for_connection(url):
    connection = __CACHE__.get(
        "{0}-{1}".format('connection', url), None
    )
    if connection is not None:
        return connection
    engine = sqla.create_engine(
        url, pool_size=20, max_overflow=0, client_encoding='utf8'
    )
    interval = 1
    while True:
        try:
            connection = engine.connect()
            __CACHE__["{0}-{1}".format('connection', url)] = connection
            LOGGER.info("Connected to database {0}".format(url))
            break
        except Exception as exc:
            LOGGER.error(exc)
            LOGGER.info("Waiting {0}s for database {1}".format(interval, url))
            time.sleep(interval)
            interval += 2
    return connection
