import logging
import operator

import sqlalchemy as sqla

from korben import config
from korben import services
from korben import etl

# temporary crap
LOGGER = logging.getLogger('korben.sync.django_initial')


def main(client=None):
    odata_metadata = services.db.poll_for_metadata(config.database_odata_url)
    django_metadata = services.db.poll_for_metadata(config.database_url)
    from korben.etl.main import from_cdms_psql  # TODO: sort out circluar dep
                                                # with sync.utils

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
        primary_key = next(
            col.name for col in table.primary_key.columns.values()
        )
        rows = odata_metadata.bind.execute(
            sqla.select([table.columns[primary_key]])
        ).fetchall()
        guids = map(operator.itemgetter(primary_key), rows)

        # the function below temporarily writes out fkey constraint fails which
        # are picked up below
        from_cdms_psql(table, tuple(guids), idempotent=True)
