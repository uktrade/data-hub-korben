import logging
import os

import sqlalchemy as sqla
from sqlalchemy.sql import functions as sqla_func

LOGGER = logging.getLogger('korben.sync.utils')
CHUNKSIZE = 1000


def file_leaf(*args):
    '''
    Where *args are str, the last str is the name of a file and the preceding
    str are path fragments, create necessary and suffcient directories for the
    file to be created at the path.
    '''
    path = os.path.join(*map(str, args))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def select_chunks(execute, basetable, select):
    'Generator yielding chunks of a select'
    count_q = sqla.select([sqla.func.count()]).select_from(basetable)
    count = execute(count_q).scalar()
    for offset in range(0, count, CHUNKSIZE):
        LOGGER.info('Evaluating chunk %s', offset)
        yield execute(select.offset(offset).limit(CHUNKSIZE)).fetchall()
