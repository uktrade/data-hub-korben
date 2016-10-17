import pytest
from korben.sync import poll


@pytest.yield_fixture
def category_object(tier0, tier0_postinitial, odata_test_service):
    category = {'ID': 123, 'Name': 'Dihedral'}
    resp = odata_test_service.create('Categories', category)
    assert resp.status_code == 201
    yield category
    odata_test_service.delete('Categories', 123)


def test_poll_create(odata_test_service, odata_fetchall, category_object):
    'Create an object in the service and check a call to `poll` is reflective'
    poll.poll(odata_test_service, against='Name')
    result = odata_fetchall(
        'SELECT "Name" FROM "Categories" WHERE "ID"={0}'.format(
            category_object['ID']
        )
    )
    assert result[0][0] == category_object['Name']


def test_poll_update(odata_test_service, odata_fetchall, category_object):
    'Update an object in the service and check a call to `poll` is reflective'
    update_dict = {'Name': 'Trihedral'}
    resp = odata_test_service.update(
        'Categories', False, category_object['ID'], update_dict,
    )
    assert resp.status_code == 200
    poll.poll(odata_test_service, against='Name')
    result = odata_fetchall(
        'SELECT "Name" FROM "Categories" WHERE "ID"={0}'.format(
            category_object['ID']
        )
    )
    assert result[0][0] == update_dict['Name']
