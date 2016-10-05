import re


def test_create_account(test_app):
    name = 'Cake Factory'
    resp = test_app.post_json('/create/company_company', {'name': name})
    match = re.match('.{8}-.{4}-.{4}-.{12}', resp.json['id'])
    assert match.span() == (0, 31)
    assert resp.json['name'] == name
