import json

from korben import config
from korben.bau import common
from korben.bau.views import SENTRY_CLIENT
from korben.bau.auth import generate_signature

EXC_MESSAGE = 'BOOM!'

class Explosion(Exception): pass

def explode(*args, **kwargs): raise Explosion(EXC_MESSAGE)

def assert_about_capture(sentry_client_instance, exc_info=None, **kwargs):
    exc = exc_info[1]
    assert isinstance(exc, Explosion)
    assert str(exc) == EXC_MESSAGE


def test_sentry_context_and_exception_view(monkeypatch, test_app):
    'Check that the Sentry client gets exception context and JSON is returned'
    monkeypatch.setattr(common, 'request_tablenames', explode)  # BOOM!
    monkeypatch.setattr(SENTRY_CLIENT, 'capture', assert_about_capture)
    with config.temporarily(datahub_secret='abc'):
        path = '/get/abc/def'
        body = {}
        signature = generate_signature(
            bytes(path, 'utf-8'),
            bytes(json.dumps(body), 'utf-8'),
            config.datahub_secret,
        )
        resp = test_app.post_json(
            path, body, headers={'X-Signature': signature}, status=500
        )
        assert resp.json['message'] == EXC_MESSAGE
