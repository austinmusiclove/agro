import pytest
from lib.mysql_interface.mysql_interface import MySQLInterface


@pytest.fixture
def db():
    return MySQLInterface()


def test_get_all_venues_returns_list(db):
    result = db.get_all_venues()
    assert isinstance(result, list)


def test_get_all_venues_has_id_and_name(db):
    result = db.get_all_venues()
    if result:
        assert "id" in result[0]
        assert "name" in result[0]


def test_get_venue_by_id_returns_dict(db):
    result = db.get_venue_by_id(1)
    assert result is isinstance(result, dict)


def test_get_venue_by_id_has_id_and_name(db):
    result = db.get_venue_by_id(1)
    if result:
        assert "id" in result
        assert "name" in result


"""
def test_get_events_by_venue_returns_list(db):
    result = db.get_events_by_venue(1)
    assert isinstance(result, list)

def test_get_events_by_venue_has_required_fields(db):
    result = db.get_events_by_venue(1)
    if result:
        assert "id" in result[0]
        assert "venue_id" in result[0]
"""
