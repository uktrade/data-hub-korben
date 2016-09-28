import pytest

import copy
import os
import time
import urllib

import django
from django import db as django_db
from django import apps as django_apps
from django.conf import settings as django_settings_module
from django.core.management import call_command as django_call_command
import psycopg2

import etl.target_models
from korben.etl import spec as etl_spec
from korben.sync import utils as sync_utils
from korben.services import db as korben_db


SQL_PUBLIC_TABLE_NAMES = '''
SELECT table_name FROM information_schema.tables
    WHERE table_schema='public';
'''

SQL_TABLE_COUNTS = '''
SELECT relname, n_live_tup FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC;
'''

TEST_PROP_KV_MAP = {
    'ODataDemo.Address': sync_utils.handle_multiprop,
    'Edm.DateTime': sync_utils.handle_datetime,
}

@pytest.yield_fixture
def odata_sync_utils():
    ORIGINAL_PROP_KV_MAP = copy.deepcopy(sync_utils.PROP_KV_MAP)
    sync_utils.PROP_KV_MAP = TEST_PROP_KV_MAP
    yield
    sync_utils.PROP_KV_MAP = ORIGINAL_PROP_KV_MAP



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
        'local': (
            ('ID', 'id'),
            ('Address_Street', 'address_street'),
            ('Address_City', 'address_city'),
            ('Address_State', 'address_state'),
            ('Address_ZipCode', 'address_zipcode'),
            ('Address_Country', 'address_country'),
            ('Concurrency', 'concurrency'),
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
    label = 'etl.target_models'


@pytest.fixture(scope='session')  # only want this getting called once
def configure_django():
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
            TargetModelsApp('etl.target_models', etl.target_models),
        ],
    }
    django_settings_module.configure(**django_settings)
    django.setup()



@pytest.yield_fixture
def tier0(odata_sync_utils, configure_django):
    'Mega-fixture for setting up tier0 databases, and cleaning them afterwards'
    print('For your information: Setup of tier0 db schemas commences')
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
    # close cached sqla connections (which block db access) and truncate tables
    for url in schema_fixtures.keys():
        korben_db.__CACHE__["{0}-{1}".format('connection', url)].close()
        truncate_public_tables(url)
    django_db.connection.close()


@pytest.yield_fixture
def tier0_postinitial(tier0):
    fixtures_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
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


@pytest.yield_fixture
def odata_fetchall():
    cursor = get_connection(os.environ['DATABASE_ODATA_URL']).cursor()

    def fetcher(sql):
        cursor.execute(sql)
        return cursor.fetchall()
    yield fetcher
    cursor.connection.close()
