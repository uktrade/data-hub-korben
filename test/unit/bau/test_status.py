from unittest.mock import Mock
from korben.cdms_api.rest import api as cdms_api


def test_status_fail(monkeypatch, test_app):
    mock_client_class = Mock()
    mock_client_instance = Mock()
    mock_response = Mock()
    mock_response.status_code = 418

    mock_client_class.return_value = mock_client_instance
    mock_client_instance.list = Mock
    mock_client_instance.list.return_value = mock_response

    monkeypatch.setattr(cdms_api, 'CDMSRestApi', mock_client_instance)
    response = test_app.get('/ping.xml', status=500)  # test will fail if this
                                                      # response is not a 500
    expected_body = '''\
<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>FALSE</status>
</pingdom_http_custom_check>
<!--database failed because 'module 'korben.config' has no attribute 'database_odata_url''-->
<!--redis failed because 'Error -2 connecting to redis:6379. Name or service not known.'-->
<!--cdms failed because 'CDMS replied with 418'-->
<!--polling failed because 'Error -2 connecting to redis:6379. Name or service not known.'-->
'''
    # there are no backends, so everything should fail
    assert response.body.decode('utf-8') == expected_body
