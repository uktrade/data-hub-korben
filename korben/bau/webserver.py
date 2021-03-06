'Configure Pyramid app, expose WSGI application object'
import os

from wsgiref.simple_server import make_server

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from korben.cdms_api.rest import api
from korben.services import db

from . import auth


DEFAULT_SETTINGS = {
    'odata_metadata': db.get_odata_metadata,
    'django_metadata': db.get_django_metadata,
    'cdms_client': api.CDMSRestApi
}


def get_app(overrides=None):
    if not overrides:
        overrides = {}
    for key in DEFAULT_SETTINGS:
        if key not in overrides:
            overrides[key] = DEFAULT_SETTINGS[key]()

    app_cfg = Configurator(root_factory=auth.Root, settings=overrides)
    app_cfg.set_authentication_policy(auth.AuthenticationPolicy())
    app_cfg.set_authorization_policy(ACLAuthorizationPolicy())
    app_cfg.set_default_permission('access')
    app_cfg.add_route('create', '/create/{django_tablename}/')
    app_cfg.add_route('update', '/update/{django_tablename}/')
    app_cfg.add_route('get', '/get/{django_tablename}/{ident}/')
    app_cfg.add_route('validate-credentials', '/auth/validate-credentials/')
    app_cfg.add_route('status', '/ping.xml')
    app_cfg.scan()
    return app_cfg.make_wsgi_app()


if not os.environ.get('UNIT_TESTS'):
    wsgi_app = get_app()


def start():
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
