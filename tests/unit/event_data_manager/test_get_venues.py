import pytest
from lib.event_data_manager.event_data_manager import EventDataManager
from tests.mocks.mock_mysql_interface import MockMySQLInterface
from lib.scraper.agro_scraper import AgroScraper


def test_get_venues_with_id(self):
    mock_db = MockMySQLInterface()
    mock_db.venues = [{"id": 1, "name": "Venue 1"}]

    scraper = AgroScraper()
    manager = EventDataManager(scraper, mock_db)

    result = manager._get_venues(venue_id=1)

    assert result == [{"id": 1, "name": "Venue 1"}]

def test_get_venues_without_id(self):
    mock_db = MockMySQLInterface()
    mock_db.venues = [{"id": 1}, {"id": 2}]

    scraper = AgroScraper()
    manager = EventDataManager(scraper, mock_db)

    result = manager._get_venues()

    assert len(result) == 2

def test_get_venues_returns_empty_when_not_found(self):
    mock_db = MockMySQLInterface()
    mock_db.venues = []

    scraper = AgroScraper()
    manager = EventDataManager(scraper, mock_db)

    result = manager._get_venues(venue_id=999)

    assert result is None
