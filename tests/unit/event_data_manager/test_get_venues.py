import pytest
from unittest.mock import MagicMock
from lib.event_data_manager.event_data_manager import EventDataManager
from tests.mocks.mock_mysql_interface import MockMySQLInterface


def create_manager(venues=None):
    mock_db = MockMySQLInterface()
    if venues is not None:
        mock_db.venues = venues

    scraper = MagicMock()
    manager = EventDataManager(scraper, mock_db)
    return manager


class TestGetVenues:
    def test_get_venues_with_id(self):
        manager = create_manager(venues=[{"id": 1, "name": "Venue 1"}])

        result = manager._get_venues(venue_id=1)

        assert result == [{"id": 1, "name": "Venue 1"}]

    def test_get_venues_without_id(self):
        manager = create_manager(venues=[{"id": 1}, {"id": 2}])

        result = manager._get_venues()

        assert len(result) == 2

    def test_get_venues_returns_empty_when_not_found(self):
        manager = create_manager(venues=[])

        result = manager._get_venues(venue_id=999)

        assert result is None
