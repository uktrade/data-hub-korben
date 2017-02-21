from unittest.mock import Mock
from korben.bau import poll


def mock_response(content):
    resp = Mock()
    resp.content = content
    resp.encoding = 'utf-8'
    return resp


def test_get_entry_list_a():
    resp = mock_response(b'{"d": {"results": [1]}}')
    assert poll.get_entry_list(resp) == [1]


def test_get_entry_list_b():
    assert poll.get_entry_list(mock_response(b'{"d": [1]}')) == [1]
