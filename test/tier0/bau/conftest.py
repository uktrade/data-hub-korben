import pytest

import collections
import json

from webtest import TestApp

from korben.bau import webserver
from korben.cdms_api.rest import api
from korben import config
from korben.bau.auth import generate_signature
from korben.bau import views


class SigningTestApp(TestApp):
    'Add support for signing auth to TestApp'

    def _signature_headers(self, path, body):
        signature = generate_signature(path, body, config.datahub_secret)
        return {'X-Signature': signature}

    def post(self, path, **kwargs):
        headers = kwargs.pop('headers', {})
        headers.update(self._signature_headers(bytes(path, 'utf-8'), b''))
        return super().post(path, headers=headers, **kwargs)

    def post_json(self, path, data, **kwargs):
        headers = kwargs.pop('headers', {})
        headers.update(
            self._signature_headers(
                bytes(path, 'utf-8'), bytes(json.dumps(data), 'utf-8')
            )
        )
        return super().post_json(
            path,
            data,
            headers=headers,
            content_type='application/json; charset=utf-8',
            **kwargs
        )


@pytest.fixture
def test_app(monkeypatch, odata_test_service, tier0_postinitial):
    monkeypatch.setattr(api, 'CDMSRestApi', lambda: odata_test_service)
    return SigningTestApp(webserver.get_app())
