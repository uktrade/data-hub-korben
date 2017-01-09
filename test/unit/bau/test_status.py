def test_status_fail(test_app):
    response = test_app.get('/ping.xml', status=500)  # test will fail if this
                                                      # response is not a 500
    expected_body = '''\
<?xml version="1.0" encoding="UTF-8"?>
<pingdom_http_custom_check>
    <status>FALSE</status>
</pingdom_http_custom_check>
<!--database failed because '???'-->
<!--redis failed because 'Error -2 connecting to redis:6379. Name or service not known.'-->
<!--cdms failed because 'module 'korben.config' has no attribute 'cdms_base_url''-->
<!--polling failed because 'Error -2 connecting to redis:6379. Name or service not known.'-->
'''
    # there are no backends, so everything should fail
    assert response.body.decode('utf-8') == expected_body
