import functools
import logging
import operator

import sqlalchemy as sqla

from korben import services
from korben import etl
from korben.cdms_api.rest.api import CDMSRestApi
from . import utils, constants

LOGGER = logging.getLogger('korben.sync.django_initial')


def django_tables_dep_order(django_metadata):
    odata_django = []
    django_fkey_deps = etl.utils.fkey_deps(django_metadata)
    for depth in sorted(django_fkey_deps.keys()):
        for table_name in django_fkey_deps[depth]:
            if table_name in etl.spec.DJANGO_LOOKUP:
                odata_django.append(
                    (etl.spec.DJANGO_LOOKUP[table_name], table_name)
                )
    return odata_django


def fetch_missing(metadata, missing, attempts=0):
    if attempts < constants.DJANGO_INITIAL_MISSING_ATTEMPTS:
        pass
    else:
        return
    client = CDMSRestApi()
    for _, django_name in django_tables_dep_order(metadata):
        guids = missing[django_name]
        if not guids:
            continue
        LOGGER.info(
            'Backfilling %s entries for %s after %s attempts',
            len(guids), django_name, attempts
        )
        table = metadata.tables[django_name]
        get_fn = functools.partial(utils.get_django, client, table.name)
        django_dicts = list(map(get_fn, guids))
        results, still_missing = etl.load.to_sqla_table_idempotent(
            table, [x for _, x in django_dicts if x]
        )
        count_non_existant = len([x for _, x in django_dicts if x is False])
        if count_non_existant:
            LOGGER.info(
                '%s has %s non-existant entries',
                django_name, count_non_existant
            )
        if still_missing:
            return fetch_missing(
                metadata, still_missing, attempts=attempts + 1
            )


def main(client=None):
    odata_metadata = services.db.get_odata_metadata()
    django_metadata = services.db.get_django_metadata()
    for odata_name, django_name in django_tables_dep_order(django_metadata):
        LOGGER.info('Dumping %s -> %s', odata_name, django_name)
        odata_table = odata_metadata.tables[odata_name]
        primary_key = etl.utils.primary_key(odata_table)
        chunks = utils.select_chunks(
            odata_metadata.bind.execute,
            odata_table,
            sqla.select([odata_table.columns[primary_key]])
        )
        for rows in chunks:
            guids = map(operator.itemgetter(primary_key), rows)
            results, missing =\
                etl.main.from_odata(odata_table, tuple(guids), idempotent=True)
            if missing:
                fetch_missing(django_metadata, missing)
