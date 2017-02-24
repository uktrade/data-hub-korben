import pytest
from unittest.mock import Mock

from korben import services
from korben.cdms_api.rest import api as cdms_api


@pytest.fixture
def mock_client(monkeypatch):
    mock_client_class = Mock()
    mock_client_instance = Mock()
    mock_response = Mock()
    mock_response.status_code = 418

    mock_client_class.return_value = mock_client_instance
    mock_client_instance.list = Mock
    mock_client_instance.list.return_value = mock_response
    monkeypatch.setattr(cdms_api, 'CDMSRestApi', mock_client_instance)


def test_status_fail(mock_client, test_app):
    response = test_app.get('/ping.xml', status=500)  # test will fail if this
                                                      # response is not a 500
    expected_body = '''\
<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>FALSE</status>
</pingdom_http_custom_check>
<!--database failed because 'module 'korben.config' has no attribute 'database_odata_url''-->
<!--cdms failed because 'CDMS replied with 418'-->
<!--polling failed because 'Heartbeat was found to be missing'-->
'''
    # there are no backends, so everything should fail
    assert response.body.decode('utf-8') == expected_body


def test_status_fail_redis(monkeypatch, mock_client, test_app):
    mock_redis = Mock()
    def mock_info():
        raise Exception('Everything went wrong')
    mock_redis.info = mock_info
    monkeypatch.setattr(services, 'redis', mock_redis)

    response = test_app.get('/ping.xml', status=500)  # test will fail if this
                                                      # response is not a 500
    expected_body = '''\
<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>FALSE</status>
</pingdom_http_custom_check>
<!--database failed because 'module 'korben.config' has no attribute 'database_odata_url''-->
<!--redis failed because 'Everything went wrong'-->
<!--cdms failed because 'CDMS replied with 418'-->
'''
    # there are no backends, so everything should fail
    assert response.body.decode('utf-8') == expected_body
