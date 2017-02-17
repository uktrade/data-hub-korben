import pytest

import datetime
import random

from korben.bau import poll
from korben.sync.traverse import traverse
from korben.services import db
from korben.etl import load


@pytest.yield_fixture
def traversables(odata_test_service):
    categories = list({'Name': chr(n), 'ID': n} for n in range(97, 100))
    products = list()
    for category in categories:
        products.extend([
            {
                'ID': category['ID'] * n,
                'ReleaseDate': datetime.datetime.now().isoformat(),
                'Rating': 0,
                'Price': '9000.1',
                'Name': category['Name'] + chr(n),
                'Category': {'ID': category['ID']},
            }
            for n in range(65, 68)
        ])
    create_responses_ok = []
    for name, objects in (('Categories', categories), ('Products', products)):
        for odata_dict in objects:
            resp = odata_test_service.create(name, odata_dict)
            create_responses_ok.append(resp.ok)
    assert all(create_responses_ok)

    odata_metadata = db.get_odata_metadata()
    retval = load.to_sqla_table(odata_metadata.tables['Categories'], categories)
    yield products, categories
    delete_responses_ok = []
    for name, objects in (('Categories', categories), ('Products', products)):
        for odata_dict in objects:
            resp = odata_test_service.delete(name, odata_dict['ID'])
            delete_responses_ok.append(resp.ok)
    # assert all(delete_responses_ok)  # TODO: figure out how to delete things



def test_traverse(tier0, odata_fetchone, odata_fetchall, odata_test_service, traversables):
    products, categories = traversables
    traversal_spec = (('Categories', 'ID'), (('Products', 'Category/ID'),),)
    traversal_results = traverse(odata_test_service, traversal_spec)
    for product in products:
        row = odata_fetchone(
            '''SELECT "Name" FROM "Products" WHERE "ID"='{0}';'''.format(
                product['ID']
            )
        )
        assert row[0] == product['Name']
