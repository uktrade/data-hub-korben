import logging
import operator

import sqlalchemy as sqla

from korben import services
from korben import etl

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
        LOGGER.info("Dumping {0} -> {1}".format(odata_name, django_name))
        table = odata_metadata.tables[odata_name]
        primary_key = etl.utils.primary_key(table)
        rows = odata_metadata.bind.execute(
            sqla.select([table.columns[primary_key]])
        ).fetchall()
        guids = map(operator.itemgetter(primary_key), rows)

        # the function below temporarily writes out fkey constraint fails which
        # are picked up below
        etl.main.from_odata(table, tuple(guids), idempotent=True)
