import pytest
from unittest.mock import Mock

from korben.bau import poll
from korben.bau.status import database, redis, cdms, polling


@pytest.mark.parametrize('status_function', (database, redis))
def test_local_status_functions(status_function):
    assert status_function() == (True, None)


def test_polling_status(tier0, odata_test_service):
    poll.poll(odata_test_service, against='Name')  # set polling heartbeat
    assert polling() == (True, None)


def test_update_category(monkeypatch, tier0, odata_test_service, test_app):
    poll.poll(odata_test_service, against='Name')  # set polling heartbeat
    response = test_app.get('/ping.xml', status=500)
    expected_body = '''\
<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>FALSE</status>
</pingdom_http_custom_check>
<!--cdms failed because 'module 'korben.config' has no attribute 'cdms_username''-->
'''
    assert response.body.decode('utf-8') == expected_body
