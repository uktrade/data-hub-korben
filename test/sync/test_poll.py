from korben.sync import poll


def test_poll(tier0, odata_test_service, tier0_postinitial, odata_fetchall):
    category = {'ID': 123, 'Name': 'Dihedral'}
    resp = odata_test_service.create('Categories', category)
    assert resp.status_code == 201
    poll.poll(odata_test_service, against='Name')
    assert odata_fetchall('SELECT "Name" FROM "Categories" WHERE "ID"=123')[0].Name == category['Name']
