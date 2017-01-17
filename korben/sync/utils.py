import json
import logging
import os

import requests
import sqlalchemy as sqla

from korben.etl import transform, load, spec, utils as etl_utils
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


def select_chunks(execute, basetable, select, chunksize=CHUNKSIZE, start=0):
    'Generator yielding chunks of a select'
    count_q = sqla.select([sqla.func.count()]).select_from(basetable)
    count = execute(count_q).scalar()
    for offset in range(start, count, chunksize):
        LOGGER.info('Evaluating chunk %s', offset)
        yield execute(select.offset(offset).limit(chunksize)).fetchall()


def get_django(client, django_tablename, guid):
    '''
    Get a single object from Django table name and GUID, either by grabbing it
    from the OData database or downloading from CDMS
    '''
    odata_tablename = spec.DJANGO_LOOKUP[django_tablename]
    odata_table = db.get_odata_metadata().tables[odata_tablename]
    odata_primary_key = etl_utils.primary_key(odata_table)
    odata_col_names = [col.name for col in odata_table.columns]
    select = sqla.select([odata_table])\
                 .where(odata_table.c[odata_primary_key] == guid)
    odata_row = odata_table.metadata.bind.execute(select).fetchone()
    if odata_row:
        return guid, transform.odata_to_django(odata_tablename, dict(odata_row))
    try:
        resp = client.get(odata_tablename, "guid'{0}'".format(guid))
    except requests.ConnectionError as exc:
        LOGGER.error(exc)
        return guid, False
    if resp.status_code == 404:
        LOGGER.info('%s %s doesn’t exist', odata_tablename, guid)
        return guid, None
    try:
        odata_dict = resp.json()['d']
    except json.JSONDecodeError as exc:
        # assume de-auth
        client.auth.setup_session(True)
        return get_django(client, django_tablename, guid)
    odata_table = db.get_odata_metadata().tables[odata_tablename]
    odata_row = utils.entry_row(odata_col_names, odata_dict)
    results, missing = load.to_sqla_table_idempotent(odata_table, [odata_row])
    assert not any(missing) and all([x.rowcount is 1 for x in results])
    return guid, transform.odata_to_django(odata_tablename, odata_dict)
