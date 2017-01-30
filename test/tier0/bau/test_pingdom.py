import pytest
from unittest.mock import Mock

from korben.bau import poll
from korben.bau.status import database, redis, cdms, polling


@pytest.mark.parametrize('status_function', (database, redis))
def test_local_status_functions(status_function):
    assert status_function() == (True, None)


def test_polling_status(tier0, odata_test_service):
    poller = poll.CDMSPoller(client=odata_test_service, against='Name')
    poller.poll_entities()
    assert polling() == (True, None)


def test_update_category(monkeypatch, tier0, odata_test_service, test_app):
    poller = poll.CDMSPoller(client=odata_test_service, against='Name')
    poller.poll_entities()
    response = test_app.get('/ping.xml', status=500)
    expected_body = '''\
<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>FALSE</status>
</pingdom_http_custom_check>
<!--cdms failed because 'CDMS replied with 404'-->
'''
    assert response.body.decode('utf-8') == expected_body
