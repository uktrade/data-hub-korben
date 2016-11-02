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


def get_app(overrides=None):
    settings = {
        'odata_metadata': db.get_odata_metadata(),
        'django_metadata': db.get_django_metadata(),
        'cdms_client': api.CDMSRestApi()
    }
    if overrides is not None:
        settings.update(overrides)

    app_cfg = Configurator(root_factory=auth.Root, settings=settings)
    app_cfg.set_authentication_policy(auth.AuthenticationPolicy())
    app_cfg.set_authorization_policy(ACLAuthorizationPolicy())
    app_cfg.set_default_permission('access')
    app_cfg.add_route('create', '/create/{django_tablename}')
    app_cfg.add_route('update', '/update/{django_tablename}')
    app_cfg.add_route('get', '/get/{django_tablename}/{ident}')
    app_cfg.scan('korben.bau.views')
    return app_cfg.make_wsgi_app()


def start():
    server = make_server('0.0.0.0', 8080, get_app())
    server.serve_forever()
