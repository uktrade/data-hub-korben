def test_update_category(test_app):
    id_val = 1
    name = 'Cakes'
    resp = test_app.post_json(
        '/update/categories', {'id': id_val, 'name': name}
    )
    assert resp.json_body['id'] == id_val
    assert resp.json_body['name'] == name
