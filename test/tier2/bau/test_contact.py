import copy
import re


def test_create_contact(test_app, django_fixtures):
    company_resp = test_app.post_json(
        '/create/company_company', django_fixtures.company,
    )
    company_id = company_resp.json['id']
    contact = copy.deepcopy(django_fixtures.contact)
    contact.update({
        'company_id': company_id,
    })
    contact_resp = test_app.post_json('/create/company_contact', contact)
    match = re.match('.{8}-.{4}-.{4}-.{12}', contact_resp.json['id'])
    assert match.span() == (0, 31)
    for name in ('first_name', 'last_name'):
        assert contact_resp.json[name] == django_fixtures.contact[name]
