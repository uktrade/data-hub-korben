import json

from korben import config
from korben.bau.auth import generate_signature

def test_auth_fail(test_app):
    with config.temporarily(datahub_secret='abc'):
        test_app.post_json(
            '/get/abc/def/', {}, headers={'X-Signature': 'xyz'}, status=403
        )


def test_auth(test_app):
    with config.temporarily(datahub_secret='abc'):
        path = '/get/abc/def/'
        body = {}
        signature = generate_signature(
            bytes(path, 'utf-8'),
            bytes(json.dumps(body), 'utf-8'),
            config.datahub_secret,
        )
        test_app.post_json(
            path, body, headers={'X-Signature': signature}, status=404
        )
