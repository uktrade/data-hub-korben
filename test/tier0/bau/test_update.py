def test_update_category(test_app):
    id_val = 1
    name = 'Cakes'
    resp = test_app.post_json(
        '/update/categories/', {'id': id_val, 'name': name}
    )
    assert resp.json_body['id'] == id_val
    assert resp.json_body['name'] == name


def test_update_supplier(test_app):
    expected = {
        'id': 1,
        'address_street': 'a',
        'address_city': 'b',
        'address_state': 'c',
        'address_zipcode': 'd',
        'address_country': 'e',
        'concurrency': 2,
    }
    resp = test_app.post_json('/update/suppliers/', expected)
    assert resp.json_body == expected


def test_update_fail(test_app):
    bad_request = {
        'id': 1,
        'concurrency': 'f',  # that’s not a number!
    }
    response = test_app.post_json('/update/suppliers/', bad_request, status=400)
    assert 'Int32' in response.json_body['error']['message']['value']
