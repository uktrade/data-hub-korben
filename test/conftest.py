import pytest

import copy

from korben.sync import utils as sync_utils

TEST_PROP_KV_MAP = {
    'ODataDemo.Address': sync_utils.handle_multiprop,
}


@pytest.yield_fixture
def odata_sync_utils():
    'Patch sync.utils for tests running against plain OData service'
    original_prop_kv_map = copy.deepcopy(sync_utils.PROP_KV_MAP)
    sync_utils.PROP_KV_MAP = TEST_PROP_KV_MAP
    yield sync_utils
    sync_utils.PROP_KV_MAP = original_prop_kv_map
