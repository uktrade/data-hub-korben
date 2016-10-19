import logging
import os

import sqlalchemy as sqla

from korben.etl import transform, load, spec
from korben.services import db
from korben import utils

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


def select_chunks(execute, basetable, select, chunksize=CHUNKSIZE):
    'Generator yielding chunks of a select'
    count_q = sqla.select([sqla.func.count()]).select_from(basetable)
    count = execute(count_q).scalar()
    for offset in range(0, count, chunksize):
        LOGGER.info('Evaluating chunk %s', offset)
        yield execute(select.offset(offset).limit(chunksize)).fetchall()


def get_django(client, django_tablename, guid):
    'Get a single object from Django table name and GUID'
    odata_tablename = spec.DJANGO_LOOKUP[django_tablename]
    resp = client.get(odata_tablename, "guid'{0}'".format(guid))
    if resp.status_code == 404:
        LOGGER.info('%s %s doesn’t exist', odata_tablename, guid)
        return
    odata_dict = resp.json()['d']
    odata_table = db.get_odata_metadata().tables[odata_tablename]
    odata_row = utils.entry_row(
        [col.name for col in odata_table.columns], odata_dict
    )
    _, missing = load.to_sqla_table_idempotent(odata_table, [odata_row])
    assert not any(missing)
    return transform.odata_to_django(odata_tablename, odata_dict)
