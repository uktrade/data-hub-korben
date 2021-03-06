from korben.etl import transform
from korben.cdms_api.rest.utils import datetime_to_cdms_datetime


DJANGO_SERVICE_DELIVERY_DATA = dict(
    id="arf",
    status_id="bar",
    service_offer_id="flankle",
    service_id="foo",
    dit_team_id="flum",
    company_id="flam",
    contact_id="flim",
    dit_advisor_id="flom",
    uk_region_id="flibble",
    sector_id="flamble",
    country_of_interest_id="fluzzle",
    date="2016-11-25T13:32:22+00:00",
    notes="bam",
    feedback="bom",
    subject="",  # this should be moved out of abstract in leeloo
)

ODATA_SERVICE_DELIVERY_INPUT_DATA = dict(
    optevia_servicedeliveryId="arf",
    optevia_ServiceDeliveryStatus={'Id': "bar"},
    optevia_ServiceOffer={'Id': "flankle"},
    optevia_Service={'Id': "foo"},
    optevia_ServiceProvider={'Id': "flum"},
    optevia_Organisation={'Id': "flam"},
    optevia_Contact={'Id': "flim"},
    optevia_Advisor={'Id': "flom"},
    CDMS_UNUSED_FIELD='unused value',
    optevia_UKRegion={'Id': "flibble"},
    optevia_Sector={'Id': "flamble"},
    optevia_LeadCountry={'Id': "fluzzle"},
    optevia_OrderDate="2016-11-25T13:32:22+00:00",
    optevia_Notes="bam",
    optevia_CustomerCommentFeedback="bom",
)

ODATA_SERVICE_DELIVERY_INPUT_DATA_INTERMEDIATE = dict(
    optevia_servicedeliveryId="arf",
    optevia_ServiceDeliveryStatus_Id="bar",
    optevia_ServiceOffer_Id="flankle",
    optevia_Service_Id="foo",
    optevia_ServiceProvider_Id="flum",
    optevia_Organisation_Id="flam",
    optevia_Contact_Id="flim",
    optevia_Advisor_Id="flom",
    CDMS_UNUSED_FIELD='unused value',
    optevia_UKRegion_Id="flibble",
    optevia_Sector_Id="flamble",
    optevia_LeadCountry_Id="fluzzle",
    optevia_OrderDate="2016-11-25T13:32:22+00:00",
    optevia_Notes="bam",
    optevia_CustomerCommentFeedback="bom",
)

DJANGO_CONTACT_DATA = dict(
    # Local fields
    id='uuid',
    last_name='LN',
    primary='primary contact',
    telephone_countrycode='1234',
    email='fake@example.com',
    address_1='1',
    address_2='2',
    address_3='3',
    address_4='4',
    address_town='town',
    address_county='county',
    address_postcode='PC',
    job_title='Jobber',

    # datetime fields
    modified_on='2016-11-25T13:32:22+00:00',
    created_on='2016-11-25T13:32:22+00:00',

    # concat fields
    telephone_number='12345',
    first_name='FN',

    # Non-flat fields
    company_id='4321',
    address_country_id='9876',
    title_id='0987',

    # Undefined fields skipped
)


ODATA_CONTACT_INPUT_DATA = dict(
    ContactId='uuid',
    LastName='LN',
    optevia_PrimaryContact='primary contact',
    optevia_CountryCode='1234',
    EMailAddress1='fake@example.com',
    optevia_Address1='1',
    optevia_Address2='2',
    optevia_Address3='3',
    optevia_Address4='4',
    optevia_TownCity='town',
    optevia_StateCounty='county',
    optevia_PostCode='PC',

    optevia_AreaCode='',
    optevia_TelephoneNumber='12345',
    FirstName='FN',
    MiddleName='',

    ModifiedOn='2016-11-25T13:32:22+00:00',
    CreatedOn='2016-11-25T13:32:22+00:00',

    ParentCustomerId=dict(
        Id='4321',
        LogicalName='account',
    ),
    JobTitle='Jobber',
    optevia_Country=dict(Id='9876'),
    optevia_Title=dict(Id='0987')
)


ODATA_OUTPUT_DATA = ODATA_CONTACT_INPUT_DATA.copy()

# Entities returned from odata use different datetime format
ODATA_OUTPUT_DATA['ModifiedOn'] = '/Date(1480080742000)/'
ODATA_OUTPUT_DATA['CreatedOn'] = '/Date(1480080742000)/'


def test_django_to_odata_contact():
    _, result = transform.django_to_odata('company_contact', DJANGO_CONTACT_DATA)
    assert result == ODATA_CONTACT_INPUT_DATA


def test_odata_to_django_contact():
    result = transform.odata_to_django('ContactSet', ODATA_OUTPUT_DATA)

    django_data = DJANGO_CONTACT_DATA.copy()
    # Add fields that should be populated by defaults
    django_data.update(dict(
        address_same_as_company=False, archived=False, archived_reason='',
    ))
    assert result == django_data


def test_django_to_odata_service_delivery():
    _, result = transform.django_to_odata(
        'interaction_servicedelivery', DJANGO_SERVICE_DELIVERY_DATA
    )
    expected = ODATA_SERVICE_DELIVERY_INPUT_DATA.copy()
    expected.pop('CDMS_UNUSED_FIELD')
    assert result == expected


def test_odata_to_django_service_delivery():
    result = transform.odata_to_django(
        'optevia_servicedeliverySet', ODATA_SERVICE_DELIVERY_INPUT_DATA
    )

    django_data = DJANGO_SERVICE_DELIVERY_DATA.copy()
    assert result == django_data


def test_odata_to_django_service_delivery_intermediate():
    result = transform.odata_to_django(
        'optevia_servicedeliverySet',
        ODATA_SERVICE_DELIVERY_INPUT_DATA_INTERMEDIATE
    )

    django_data = DJANGO_SERVICE_DELIVERY_DATA.copy()
    assert result == django_data


def test_round_trip_for_concat():
    original_result = transform.odata_to_django('ContactSet', ODATA_OUTPUT_DATA)
    _, result_interim = transform.django_to_odata('company_contact', original_result)

    # We need to convert datetime format here
    result_interim['ModifiedOn'] = datetime_to_cdms_datetime(result_interim['ModifiedOn'])
    result_interim['CreatedOn'] = datetime_to_cdms_datetime(result_interim['CreatedOn'])

    end_result = transform.odata_to_django('ContactSet', result_interim)

    assert end_result == original_result
