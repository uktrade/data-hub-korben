'Try to load Django fixtures into CDMS idempotently'
import logging
import yaml
from korben.etl import transform, spec
from korben.cdms_api.rest.api import CDMSRestApi
from korben.bau.views import fmt_guid


LOGGER = logging.getLogger('korben.sync.cdms_initial')


def transform_django_fixture_to_odata(client, django_fixture):
    odata_tups = []
    for django_fixture_dict in django_fixture:
        django_tablename = '_'.join(django_fixture_dict['model'].split('.'))
        guid = django_fixture_dict['pk']
        django_dict = django_fixture_dict['fields']
        django_dict.update({'id': guid})
        odata_tablename = spec.DJANGO_LOOKUP[django_tablename]
        if not client.exists(odata_tablename, fmt_guid(guid)):
            _, odata_dict =\
                transform.django_to_odata(django_tablename, django_dict)
            odata_tups.append((odata_tablename, odata_dict))
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
