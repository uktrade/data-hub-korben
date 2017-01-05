import pytest

from korben.bau import poll
from korben.bau.status import database, redis, cdms, polling


@pytest.mark.parametrize('status_function', (database, redis))
def test_local_status_functions(status_function):
    assert status_function() == (True, None)


def test_polling_status(tier0, odata_test_service):
    poll.poll(odata_test_service, against='Name')  # set polling heartbeat
    assert polling() == (True, None)
