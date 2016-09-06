import logging
import time
import sqlalchemy as sqla

LOGGER = logging.getLogger('korben.db')

def poll_for_engine():
    try:
        return sqla.create_engine(
            'postgresql://postgres:postgres@postgres/cdms_psql',
            pool_size=20,
            max_overflow=0
        )
    except sqla.exc.OperationalError:
        LOGGER.info('Waiting for database')
        time.sleep(1)
        return poll_for_engine()
