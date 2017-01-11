import sqlalchemy as sqla

from korben import services
from korben.bau import leeloo
from korben.etl import transform
from korben.sync.utils import select_chunks


def sync(odata_tablename, odata_pkey, django_tablename, failure_fmt):
    odata_metadata = services.db.get_odata_metadata()
    odata_table = odata_metadata.tables[odata_tablename]
    django_metadata = services.db.get_django_metadata()
    django_table = django_metadata.tables[django_tablename]
    odata_chunks = select_chunks(
        odata_metadata.bind.execute,
        odata_table,
        sqla.select([odata_table])
    )

    for odata_chunk in odata_chunks:
        for odata_row in odata_chunk:
            comparitor = django_table.c.id == getattr(odata_row, odata_pkey)
            select = sqla.select([django_table]).where(comparitor)
            result = django_metadata.bind.execute(select).fetchone()
            if result is not None:
                continue
            django_dict = {
                k: str(v) for k, v in
                transform.odata_to_django(odata_tablename, dict(odata_row)).items()
            }
            response = leeloo.send(django_tablename, [django_dict])[0]
            if response.status_code != 200:
                services.redis.set(
                    failure_fmt.format(getattr(odata_row, odata_pkey)),
                    response.content.decode(response.encoding)
                )

def main():
    entity_specs = (
        (
            'AccountSet',
            'AccountId',
            'company_company',
            'company-failures/{0}'
        ),
        (
            'ContactSet',
            'ContactId',
            'company_contanct',
            'contact-failures/{0}'
        ),
        (
            'detica_interactionSet',
            'ActivityId',
            'company_interaction',
            'interaction-failures/{0}'
        ),
    )
    for entity_spec in entity_specs:
        sync(*entity_spec)
