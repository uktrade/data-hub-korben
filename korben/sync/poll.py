from ..cdms_api.rest.api import CDMSRestApi
import sqlalchemy as sqla

def entity():
    cdms_client = CDMSRestApi()

def main(resp_dir, entity_name):
    engine = sqla.create_engine('postgresql://localhost/cdms_psql')
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    tempfiles, proc = main(metadata, resp_dir, entity_name)
    proc.wait()
