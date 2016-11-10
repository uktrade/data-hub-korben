import re


def test_create_company(test_app, django_company):
    resp = test_app.post_json('/create/company_company', django_company)
    match = re.match('.{8}-.{4}-.{4}-.{12}', resp.json['id'])
    assert match.span() == (0, 31)
    assert resp.json['name'] == django_company['name']
