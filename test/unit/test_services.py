from korben.services.db_manager import DatabaseManager


def test_dbmanager_singleton():
    a = DatabaseManager()
    b = DatabaseManager()
    for instance in (a, b):
        assert instance.connections == {}
        assert instance.metadatas == {}
    assert a == b
