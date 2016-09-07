import logging
import time
import sqlalchemy as sqla

LOGGER = logging.getLogger('korben.db')
logging.basicConfig(level=logging.INFO)

ENGINE = sqla.create_engine(
    'postgresql://postgres:postgres@postgres/cdms_psql',
    pool_size=20,
    max_overflow=0
)


def poll_for_connection():
    interval = 1
    while True:
        try:
            connection = ENGINE.connect()
            LOGGER.info('Connected to database')
            break
        except Exception as exc:
            LOGGER.error(exc)
            LOGGER.info("Waiting {0}s for database".format(interval))
            time.sleep(interval)
            interval += 2
    return connection
