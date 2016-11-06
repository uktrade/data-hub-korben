import pytest

import copy
import json
import os
import time
import urllib

import django
import psycopg2
import requests

from django import apps as django_apps
from django import db as django_db
from django.conf import settings as django_settings_module
from lxml import etree

from korben import config
from korben.cdms_api.rest import api
from korben.cdms_api.rest.auth.noop import NoopAuth
from korben.etl import spec as etl_spec
from korben import services
from korben.bau import poll
from korben.bau import leeloo
from korben.sync.scrape import constants as scrape_constants


ATOM_PREFIX = '{http://www.w3.org/XML/1998/namespace}'
ODATA_URL = 'http://services.odata.org/V2/(S(readwrite))/OData/OData.svc/'
SQL_PUBLIC_TABLE_NAMES = '''
SELECT table_name FROM information_schema.tables
    WHERE table_schema='public';
'''
SQL_TABLE_COUNTS = '''
SELECT relname, n_live_tup FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC;
'''


@pytest.fixture(scope='session')
def odata_test_service():
    resp = requests.get(ODATA_URL)
    root = etree.fromstring(resp.content)
    config.cdms_base_url = root.attrib[ATOM_PREFIX + 'base']
    client = api.CDMSRestApi(NoopAuth())
    return client


TEST_MAPPINGS = {
    'Categories': {
        'to': 'categories',
        'local': (
            ('ID', 'id'),
            ('Name', 'name'),
        )
    },
    'Suppliers': {
        'to': 'suppliers',
        'etag': True,
        'local': (
            ('ID', 'id'),
            ('Concurrency', 'concurrency'),
        ),
        'nonflat': (
            (
                'Address',
                (
                    ('Street', 'address_street'),
                    ('City', 'address_city'),
                    ('State', 'address_state'),
                    ('ZipCode', 'address_zipcode'),
                    ('Country', 'address_country'),
                ),
            ),
        ),
    },
    'Products': {
        'to': 'products',
        'local': (
            ('ID', 'id'),
            ('ReleaseDate', 'release_date'),
            ('Rating', 'rating'),
            ('Price', 'price'),
            ('Name', 'name'),
            ('Description', 'description'),
            ('ReleaseDate', 'release_date'),
            ('DiscontinuedDate', 'discontinued_date'),
            ('Rating', 'rating'),
            ('Price', 'price'),
            (
                'Products_Category_Categories_ID',
                'products_category_categories_id',
            ),
            (
                'Products_Supplier_Suppliers_ID',
                'products_supplier_suppliers_id',
            ),
        ),
    },
}


def get_connection(url):
    while True:
        try:
            return psycopg2.connect(url)
        except psycopg2.OperationalError as exc:
            time.sleep(1)


def execute_ignore_existing(cursor, sql):
    try:
        cursor.execute(sql)
        cursor.connection.commit()
    except psycopg2.ProgrammingError as exc:
        if 'already exists' not in exc.pgerror:
            raise
        cursor.connection.rollback()


def truncate_public_tables(url):
    cursor = get_connection(url).cursor()
    cursor.execute(SQL_PUBLIC_TABLE_NAMES)
    public_table_names = cursor.fetchall()
    for (table_name,) in public_table_names:
        cursor.execute('TRUNCATE "{0}" CASCADE;'.format(table_name))
        cursor.connection.commit()
    table_counts = []
    for (table_name,) in public_table_names:
        cursor.execute('SELECT count(*) FROM "{0}"'.format(table_name))
        table_counts.append(cursor.fetchone())
    cursor.connection.close()
    assert sum([count for (count,) in table_counts]) == 0


class TargetModelsApp(django_apps.AppConfig):
    label = 'target_models'


@pytest.fixture(scope='session')  # only want this getting called once
def configure_django():
    import target_models
    django_db_url = urllib.parse.urlparse(os.environ['DATABASE_URL'])
    django_settings = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': django_db_url.hostname,
                'NAME': django_db_url.path.lstrip('/'),
                'USER': django_db_url.username,
            }
        },
        'INSTALLED_APPS': [
            TargetModelsApp('target_models', target_models),
        ],
    }
    django_settings_module.configure(**django_settings)
    django.setup()


@pytest.fixture(scope='session')
def django_models():
    from target_models import models
    return models


@pytest.yield_fixture
def tier0(monkeypatch, odata_utils, configure_django):
    'Mega-fixture for setting up tier0 databases, and cleaning them afterwards'

    # patch for differing resp format
    def get_entry_list(resp):
        resp_json = json.loads(resp.content.decode(resp.encoding or 'utf-8'))
        return resp_json['d']
    monkeypatch.setattr(poll, 'get_entry_list', get_entry_list)

    # not testing leeloo here
    monkeypatch.setattr(leeloo, 'send', lambda *a, **b: None)

    # tone down scrape
    monkeypatch.setattr(scrape_constants, 'PROCESSES', 4)
    monkeypatch.setattr(scrape_constants, 'CHUNKSIZE', 1)

    fixtures_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
    schema_fixtures = {
        os.environ['DATABASE_ODATA_URL']: (
            'test-create.sql', 'test-alter.sql'
        ),
        os.environ['DATABASE_URL']: ('test-django.sql',),
    }

    for url, filenames in schema_fixtures.items():
        cursor = get_connection(url).cursor()
        for name in filenames:
            with open(os.path.join(fixtures_path, name), 'r') as sql_fh:
                execute_ignore_existing(cursor, sql_fh.read())
        cursor.connection.close()


    # overwrite etl spec things
    ORIGINAL_MAPPINGS = copy.deepcopy(etl_spec.MAPPINGS)
    etl_spec.MAPPINGS = TEST_MAPPINGS
    etl_spec.DJANGO_LOOKUP = {
        mapping['to']: name for name, mapping in TEST_MAPPINGS.items()
    }
    yield  # kick out to run the test here
    # return etl spec
    etl_spec.MAPPINGS = ORIGINAL_MAPPINGS
    etl_spec.DJANGO_LOOKUP = {
        mapping['to']: name for name, mapping in ORIGINAL_MAPPINGS.items()
    }
    services.db.reset_connections()
    # truncate tables
    for url in schema_fixtures.keys():
        truncate_public_tables(url)


@pytest.yield_fixture
def tier0_postinitial(tier0):
    fixtures_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'fixtures',
    )
    fixture_spec = (
        (os.environ['DATABASE_ODATA_URL'], 'odata-initial.sql'),
        (os.environ['DATABASE_URL'], 'odata-initial-django.sql'),
    )

    for url, fixture_name in fixture_spec:
        cursor = get_connection(url).cursor()
        with open(os.path.join(fixtures_path, fixture_name), 'r') as sql_fh:
            cursor.execute(sql_fh.read())
            cursor.connection.commit()
        cursor.connection.close()


@pytest.fixture(scope='session')
def odata_fetchall():

    def fetcher(sql):
        connection = get_connection(os.environ['DATABASE_ODATA_URL'])
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        return result

    return fetcher
