from pyramid import httpexceptions as http_exc
from pyramid.authentication import RemoteUserAuthenticationPolicy, BasicAuthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.response import Response
from wsgiref.simple_server import make_server

from korben import config
from korben.cdms_api.rest import api
from korben.etl import spec, transform, utils
from korben.services import db

from . import auth
from . import views


WSGI_APP = None


DEFAULT_SETTINGS = {
    'odata_metadata': lambda: db.get_odata_metadata(),
    'django_metadata': lambda: db.get_django_metadata(),
    'cdms_client': lambda: api.CDMSRestApi()
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


def wsgi_app(environ, start_request):
    """Wrapper for WSGI app with delayed instantiation"""
    global WSGI_APP
    if WSGI_APP is None:
        WSGI_APP = get_app()

    return WSGI_APP(environ, start_request)


def start():
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
