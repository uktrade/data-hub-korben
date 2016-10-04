import pytest

import copy

from korben import utils

TEST_PROP_KV_MAP = {
    'ODataDemo.Address': utils.handle_multiprop,
}


@pytest.yield_fixture
def odata_utils():
    'Patch sync.utils for tests running against plain OData service'
    original_prop_kv_map = copy.deepcopy(utils.PROP_KV_MAP)
    utils.PROP_KV_MAP = TEST_PROP_KV_MAP
    yield utils
    utils.PROP_KV_MAP = original_prop_kv_map
