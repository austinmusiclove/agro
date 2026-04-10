import pytest
from dotenv import load_dotenv
from lib.event_data_manager.event_data_manager import EventDataManager
from tests.mocks.mock_mysql_interface import MockMySQLInterface
from lib.scraper.agro_scraper import AgroScraper
from lib.fetcher.factory import FetcherFactory
from lib.data_extractor.factory import DataExtractorFactory
from lib.config import YamlConfigLoader


@pytest.mark.integration
@pytest.mark.costly
def test_scrape_event_list_pages_with_agro_scraper():
    load_dotenv(override=True)

    # Setup mock MySQL interface with venue 53
    mock_mysql = MockMySQLInterface()
    mock_mysql.venues = [
        {"id": 53, "name": "Antone's Nightclub", "website_events_url": "https://austinmusiclove.github.io/agro/antonesnightclub_page1.html"}
    ]
    mock_mysql.events = []  # No existing events

    # Setup mock image saver
    class MockImageSaver:
        def __init__(self):
            self.saved_images = []

        def save(self, image_bytes, name_hint=None):
            self.saved_images.append({"bytes": len(image_bytes), "hint": name_hint})
            return f"/mock/path/{name_hint or 'image'}"

    mock_image_saver = MockImageSaver()

    # Create AgroScraper
    config_loader = YamlConfigLoader()
    fetcher_factory = FetcherFactory(config_loader)
    data_extractor_factory = DataExtractorFactory(config_loader)
    scraper = AgroScraper(fetcher_factory, data_extractor_factory, config_loader)

    # Create EventDataManager
    event_data_manager = EventDataManager(scraper, mock_mysql, mock_image_saver)

    # Execute
    event_data_manager.scrape_event_list_pages(venue_id=53)

    # Assert
    assert len(mock_mysql.get_future_events_calls) > 0, "get_future_events_by_venue should have been called"
    assert len(mock_mysql.saved_transactions) > 0, "save_transaction should have been called"

    # With pagination, we expect 68 events
    assert len(mock_mysql.saved_transactions) == 68, f"Expected 68 transactions, got {len(mock_mysql.saved_transactions)}"

    # Verify screenshots were saved
    assert len(mock_image_saver.saved_images) > 0, "Screenshots should have been saved"

    # Verify first transaction has expected structure
    first_txn = mock_mysql.saved_transactions[0]
    assert first_txn["target_table"] == "events"
    assert "data" in first_txn
    assert "txn_data" in first_txn
    assert first_txn["txn_data"]["transaction_type"] == "create"
