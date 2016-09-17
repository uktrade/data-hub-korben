import logging
import operator

import sqlalchemy as sqla

from korben import config
from korben import services
from korben import etl

LOGGER = logging.getLogger('korben.sync.django_initial')


def main():
    from korben.etl.main import from_cdms_psql  # TODO: sort out circluar dep with sync.utils
    odata_metadata = services.db.poll_for_metadata(config.database_odata_url)
    django_metadata = services.db.poll_for_metadata(config.database_url)

    odata_tables = []
    django_fkey_deps = etl.utils.fkey_deps(django_metadata)
    for depth in sorted(django_fkey_deps.keys()):
        for table_name in django_fkey_deps[depth]:
            if table_name in etl.spec.DJANGO_LOOKUP:
                odata_tables.append(etl.spec.DJANGO_LOOKUP[table_name])
    for name in odata_tables:
        LOGGER.info("Dumping OData to Django for {0}".format(name))
        table = odata_metadata.tables[name]
        primary_key = next(
            col.name for col in table.primary_key.columns.values()
        )
        rows = odata_metadata.bind.execute(
            sqla.select([table.columns[primary_key]])
        ).fetchall()
        guids = map(operator.itemgetter(primary_key), rows)
        from_cdms_psql(table, guids, idempotent=True)
