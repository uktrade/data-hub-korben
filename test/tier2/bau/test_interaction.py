import copy
import re


def test_create_interaction(test_app, django_fixtures):
    company_resp = test_app.post_json(
        '/create/company_company', django_fixtures.company,
    )
    company_id = company_resp.json['id']
    contact = copy.deepcopy(django_fixtures.contact)
    contact.update({'company_id': company_id})
    contact_resp = test_app.post_json('/create/company_contact', contact)
    contact_id = contact_resp.json['id']
    interaction = copy.deepcopy(django_fixtures.interaction)
    interaction_update = {
        'dit_advisor_id': django_fixtures.advisor['id'],
        'contact_id': contact_id,
        'company_id': company_id,
    }
    interaction.update(interaction_update)
    interaction_resp = test_app.post_json(
        '/create/interaction_interaction', interaction
    )
    match = re.match('.{8}-.{4}-.{4}-.{12}', interaction_resp.json['id'])
    assert match.span() == (0, 31)
    for name, expected in interaction_update.items():
        assert interaction_resp.json[name] == expected


def test_get_interaction_date(test_app, django_fixtures):
    'Check that the date comes back in a non-CDMS format'
    interaction_resp = test_app.post_json(
        '/get/interaction_interaction/f0b138b8-18e6-e511-8ffa-e4115bead28a', {}
    )
    assert '/Date(' not in interaction_resp.json['date']
