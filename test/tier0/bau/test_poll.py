import pytest
from korben.bau import poll


@pytest.yield_fixture
def category_object(tier0, tier0_postinitial, odata_test_service):
    category = {'ID': 123, 'Name': 'Dihedral'}
    resp = odata_test_service.create('Categories', category)
    assert resp.status_code == 201
    yield category
    odata_test_service.delete('Categories', 123).ok


def test_poll_create(odata_test_service, odata_fetchall, category_object):
    'Create an object in the service and check a call to `poll` is reflective'
    poller = poll.CDMSPoller(client=odata_test_service, against='Name')
    poller.poll_entities()
    result = odata_fetchall(
        'SELECT "Name" FROM "Categories" WHERE "ID"={0}'.format(
            category_object['ID']
        )
    )
    assert result[0][0] == category_object['Name']


def test_poll_update(odata_test_service, odata_fetchall, category_object):
    'Update an object in the service and check a call to `poll` is reflective'
    update_dict = {'Name': 'Trihedral'}
    poller = poll.CDMSPoller(client=odata_test_service, against='Name')
    poller.poll_entities()
    resp = odata_test_service.update(
        'Categories', False, category_object['ID'], update_dict,
    )
    assert resp.status_code == 200
    poller.poll_entities()
    result = odata_fetchall(
        'SELECT "Name" FROM "Categories" WHERE "ID"={0}'.format(
            category_object['ID']
        )
    )
    assert result[0][0] == update_dict['Name']


@pytest.yield_fixture
def ten_categories(monkeypatch, tier0, tier0_postinitial, odata_test_service):
    # should result in five pages of polling
    monkeypatch.setattr(poll.CDMSPoller, 'PAGE_SIZE', 2)

    categories = [
        {'ID': id_, 'Name': 'One of ten'} for id_ in range(9000, 9010)
    ]
    for category in categories:
        resp = odata_test_service.create('Categories', category)
        assert resp.status_code == 201
    yield categories
    for category in categories:
        resp = odata_test_service.delete('Categories', category['ID'])
        assert resp.status_code == 204


def test_poll_paging(ten_categories, odata_test_service, odata_fetchall):
    poller = poll.CDMSPoller(client=odata_test_service, against='Name')
    poller.poll_entities()
    ids = [x['ID'] for x in ten_categories]
    in_clause = "({0})".format(','.join(map(str, ids)))

    result = odata_fetchall(
        'SELECT "ID" FROM "Categories" WHERE "ID" IN {0}'.format(in_clause)
    )
    assert set(map(int, [x[0] for x in result])) == set(ids)
