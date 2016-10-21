import pytest

import collections
import datetime

from webtest import TestApp

from korben.bau import webserver
from korben.cdms_api.rest import api


@pytest.fixture
def test_app():
    app = webserver.get_app()
    return TestApp(app)


@pytest.fixture
def django_company():
    'A company model as it would be sent from Django, sans non-enum fkeys'
    return {
        'name': 'Aguirre, der Zorn Gottes',
        'registered_address_1': '1 The Rapids',
        'registered_address_town': 'El Dorado',
        # Peru
        'registered_address_country_id': '5061b8be-5d95-e211-a939-e4115bead28a',
        'company_number': '01234567',
        # Company
        'business_type_id': '98d14e94-5d95-e211-a939-e4115bead28a',
        # Metals, Minerals and Materials : Metals
        'sector_id': '6af1690c-6095-e211-a939-e4115bead28a',
        # Sark
        'uk_region_id': '914cd12a-6095-e211-a939-e4115bead28a',
    }


@pytest.fixture
def django_contact():
    'A contact model as it would be sent from Django, sans non-enum fkeys'
    return {
        # HRH
        'title': 'c0d9b924-6095-e211-a939-e4115bead28a',
        'first_name': 'Klaus', 'last_name': 'Kinski',
        # Unknown
        'role_id': '6d756b9a-5d95-e211-a939-e4115bead28a',
        'telephone_countrycode': '+51',
        'telephone_number': '123456',
        'email': 'klaus.kinski@thekinskis.com',
        'registered_address_1': '1 The Rapids',
        'registered_address_town': 'El Dorado',
        # Peru
        'registered_address_country_id': '5061b8be-5d95-e211-a939-e4115bead28a',
        # Sark
        'uk_region_id': '914cd12a-6095-e211-a939-e4115bead28a',
    }


@pytest.fixture
def django_interaction():
    'An interaction model as it would be sent from Django, sans non-enum fkeys'
    return {
        # Face to Face
        'interaction_type_id': 'a5d71fdd-5d95-e211-a939-e4115bead28a',
        'subject': 'Pros and cons of shooting production assistants',
        'date_of_interaction': str(datetime.datetime.now()),
        'notes': 'We decided we shouldn’t play with guns in the future.',
        # Trade - Enquiry
        'service_id': '330bba2b-3499-e211-a939-e4115bead28a',
        # British Embassy Lima Peru
        'dit_team_id': '5b6e1abc-9698-e211-a939-e4115bead28a',
    }


@pytest.fixture
def django_fixtures(
        django_advisor, django_company, django_contact, django_interaction
    ):
    'All the models in Django format'
    spec = {
        'advisor': django_advisor,
        'company': django_company,
        'contact': django_contact,
        'interaction': django_interaction,
    }
    spec_nt = collections.namedtuple('fixtures', spec.keys())
    return spec_nt(**spec)
