'Try to load Django fixtures into CDMS idempotently'
import logging
import yaml
from korben.etl import transform, spec
from korben.cdms_api.rest.api import CDMSRestApi
from korben.bau.views import fmt_guid


LOGGER = logging.getLogger('korben.sync.cdms_initial')


def transform_django_fixture_to_odata(client, django_fixture):
    odata_tups = []
    for django_dict in django_fixture:
        django_tablename = django_dict['model'].split('.').join('_')
        name, guid = django_dict['name'], django_dict['pk']
        odata_tablename = spec.DJANGO_LOOKUP[django_tablename]
        if not client.exists(odata_tablename, fmt_guid(guid)):
            odata_tup = (
                odata_tablename,
                transform.django_to_odata(
                    django_tablename, {'id': guid, 'name': name}
                )
            )
            odata_tups.append(odata_tup)
        else:
            LOGGER.info(
                "%s with id %s already exists in CDMS", django_tablename, guid
            )
    return odata_tups


def send_django_fixture_to_cdms(name):
    with open(name) as yaml_fh:
        django_fixture = yaml.load(yaml_fh.read())
    client = CDMSRestApi()
    odata_dicts = transform_django_fixture_to_odata(client, django_fixture)
    for odata_tablename, odata_dict in odata_dicts:
        resp = client.create(odata_tablename, odata_dict)
        assert resp.ok


def main(*names):
    for name in names:
        send_django_fixture_to_cdms(name)
