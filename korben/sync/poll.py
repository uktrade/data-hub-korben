from lxml import etree
import sqlalchemy as sqla
from ..cdms_api.rest.api import CDMSRestApi
from . import resp_csv
from . import constants
from . import utils

def main(entity_name):
    cdms_api = CDMSRestApi()
    engine = sqla.create_engine('postgresql://localhost/cdms_psql')
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    table = metadata.tables[entity_name + 'Set']
    col_names = [x.name for x in table.columns]
    # assume a single column
    primary_key = next(col.name for col in table.primary_key.columns.values())
    resp = cdms_api.list(entity_name, order_by='ModifiedOn')
    rows = []
    for entry in etree.fromstring(resp.content).iter(constants.ENTRY_TAG):
        rows.append(utils.entry_row(col_names, None, entry))
    for row in rows:
        in_db = (
            table.select()
                 .where(table.columns[primary_key] == row[primary_key])
                 .execute()
                 .fetchone()
        )
        if in_db:
            import ipdb;ipdb.set_trace()
            pass

        pass
