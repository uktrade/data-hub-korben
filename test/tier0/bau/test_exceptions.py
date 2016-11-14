import pytest


def test_404_json(test_app):
    '404 should be JSON'
    resp = test_app.get('/', status=404)
    assert resp.content_type == 'application/json'
    assert resp.json_body == {'message': '/'}


@pytest.mark.parametrize('route_name', ('create', 'update'))
def test_bad_table_404_json(test_app, route_name):
    'Unsupported table name should 404 with JSON'
    not_a_table = 'cake'
    resp = test_app.post_json(
        '/{0}/{1}/'.format(route_name, not_a_table), {}, status=404
    )
    assert resp.content_type == 'application/json'
    assert not_a_table in resp.json_body['message']


@pytest.mark.parametrize('route_name', ('create', 'update'))
def test_ok_table_no_json(test_app, route_name):
    'Unsupported table name should 404 with JSON'
    resp = test_app.post('/{0}/suppliers/'.format(route_name), status=400)
    assert resp.content_type == 'application/json'
    assert resp.json_body['message'] == 'Invalid JSON'
