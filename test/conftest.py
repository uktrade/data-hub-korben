import os
import time
import urllib

import django
from django import apps as django_apps
from django.conf import settings as django_settings
from django.core.management import call_command as django_call_command
import psycopg2

import etl.target_models

def get_connection(url):
    while True:
        try:
            return psycopg2.connect(url)
        except psycopg2.OperationalError as exc:
            time.sleep(1)


def try_execute(cursor, sql):
    try:
        cursor.execute(sql)
    except psycopg2.ProgrammingError as exc:
        if 'already exists' not in exc.pgerror:
            raise
        cursor.connection.rollback()

print('Initialising databases for tier-0')

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
SCHEMA_FIXTURES = {
    os.environ['DATABASE_ODATA_URL']: ('test-create.sql', 'test-alter.sql'),
    os.environ['DATABASE_URL']:       ('test-django.sql',),
}

for url, filenames in SCHEMA_FIXTURES.items():
    cursor = get_connection(url).cursor()
    for name in filenames:
        with open(os.path.join(FIXTURES_PATH, name), 'r') as sql_fh:
            try_execute(cursor, sql_fh.read())
    cursor.connection.commit()
    cursor.connection.close()


class TargetModelsApp(django_apps.AppConfig):
    label = 'etl.target_models'


DATABASE_URL = urllib.parse.urlparse(os.environ['DATABASE_URL'])

DJANGO_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': DATABASE_URL.hostname,
            'NAME': DATABASE_URL.path.lstrip('/'),
            'USER': DATABASE_URL.username,
        }
    },
    'INSTALLED_APPS': [
        TargetModelsApp('etl.target_models', etl.target_models),
    ],
}
django_settings.configure(**DJANGO_SETTINGS)
django.setup()
