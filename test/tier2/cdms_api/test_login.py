def test_cdms_client_logged_in(cdms_client, credentials):
    'Test that the CDMSRestApi successfully logs in all test users'
    client = cdms_client(*credentials)
    client.list('BusinessUnitSet')
