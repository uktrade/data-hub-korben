import sqlalchemy as sqla

from korben import services
from korben.bau import leeloo
from korben.etl import transform
from korben.sync.utils import select_chunks


odata_tablename = 'detica_interactionSet'
odata_metadata = services.db.get_odata_metadata()
odata_table = odata_metadata.tables[odata_tablename]
django_tablename = 'company_interaction'
django_metadata = services.db.get_django_metadata()
django_table = django_metadata.tables[django_tablename]


odata_chunks = select_chunks(
    odata_metadata.bind.execute,
    odata_table,
    sqla.select([odata_table]).limit(2000)
)

for odata_chunk in odata_chunks:
    for odata_row in odata_chunk:
        result = django_metadata.bind.execute(
            sqla.select([django_table])\
                .where(django_table.c.id==odata_row.ActivityId)
        ).fetchone()
        if result is not None:
            continue
        django_dict = {
            k: str(v) for k, v in
            transform.odata_to_django(odata_tablename, dict(odata_row)).items()
        }
        response = leeloo.send('company_interaction', [django_dict])[0]
        if response.status_code != 200:
            services.redis.set(
                "interaction-failures/{0}".format(odata_row.ActivityId),
                response.content.decode(response.encoding)
            )
