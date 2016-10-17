import logging
import operator

import sqlalchemy as sqla

from korben import services
from korben import etl
from . import utils

# temporary crap
LOGGER = logging.getLogger('korben.sync.django_initial')


def main(client=None):
    odata_metadata = services.db.get_odata_metadata()
    django_metadata = services.db.get_django_metadata()
    odata_django = []
    django_fkey_deps = etl.utils.fkey_deps(django_metadata)
    for depth in sorted(django_fkey_deps.keys()):
        for table_name in django_fkey_deps[depth]:
            if table_name in etl.spec.DJANGO_LOOKUP:
                odata_django.append(
                    (etl.spec.DJANGO_LOOKUP[table_name], table_name)
                )
    for odata_name, django_name in odata_django:
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
            etl.main.from_odata(odata_table, tuple(guids), idempotent=True)
