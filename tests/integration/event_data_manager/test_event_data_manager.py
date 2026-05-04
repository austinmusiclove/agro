import pytest
from dotenv import load_dotenv
from lib.event_data_manager.event_data_manager import EventDataManager
from tests.mocks.mock_mysql_interface import MockMySQLInterface
from lib.scraper.agro_scraper import AgroScraper
from lib.fetcher.factory import FetcherFactory
from lib.data_extractor.factory import DataExtractorFactory
from lib.image_saver.factory import ImageSaverFactory
from lib.config import YamlConfigLoader


@pytest.fixture
def config_loader():
    load_dotenv(override=True)
    return YamlConfigLoader()


@pytest.fixture
def image_saver(config_loader):
    factory = ImageSaverFactory(config_loader)
    return factory.create()


@pytest.fixture(autouse=True)
def cleanup_s3_uploads(image_saver):
    if not hasattr(image_saver, '_s3_client'):
        yield
        return

    uploaded_keys = []
    image_saver._save_call_count = 0

    original_save = image_saver.save

    def tracked_save(image_bytes, name_hint=None):
        image_saver._save_call_count += 1
        result = original_save(image_bytes, name_hint)
        if "s3://" in result:
            key = result.replace(f"s3://{image_saver._bucket}/", "")
        else:
            parts = result.split(f".s3.{image_saver._region}.amazonaws.com/")
            key = parts[1] if len(parts) > 1 else result.split("/")[-1]
        uploaded_keys.append(key)
        return result

    image_saver.save = tracked_save

    yield

    for key in uploaded_keys:
        try:
            image_saver._s3_client.delete_object(Bucket=image_saver._bucket, Key=key)
        except Exception:
            pass


@pytest.mark.integration
@pytest.mark.costly
def test_scrape_event_list_pages_with_agro_scraper(config_loader, image_saver):
    load_dotenv(override=True)

    # Setup mock MySQL interface with venue 53
    mock_mysql = MockMySQLInterface()
    mock_mysql.venues = [
        {"id": 53, "name": "Antone's Nightclub", "website_events_url": "https://austinmusiclove.github.io/agro/antonesnightclub_page1.html"}
    ]
    mock_mysql.events = []  # No existing events

    # Create AgroScraper
    fetcher_factory = FetcherFactory(config_loader)
    data_extractor_factory = DataExtractorFactory(config_loader)
    scraper = AgroScraper(fetcher_factory, data_extractor_factory, config_loader)

    # Create EventDataManager
    event_data_manager = EventDataManager(scraper, mock_mysql, image_saver)

    # Execute
    event_data_manager.scrape_event_list_pages(venue_id=53, paginate=True)

    # Assert
    assert len(mock_mysql.get_future_events_calls) > 0, "get_future_events_by_venue should have been called"
    assert len(mock_mysql.saved_transactions) > 0, "save_transaction should have been called"

    # With pagination, we expect 68 events
    assert len(mock_mysql.saved_transactions) == 68, f"Expected 68 transactions, got {len(mock_mysql.saved_transactions)}"

    # Verify screenshots were saved (should be called once - same screenshot reused for all events)
    assert image_saver._save_call_count >= 4, f"Expected 4 screenshot saves, got {image_saver._save_call_count}"

    # Verify first transaction has expected structure
    first_txn = mock_mysql.saved_transactions[0]
    assert first_txn["target_table"] == "events"
    assert "data" in first_txn
    assert "txn_data" in first_txn
    assert first_txn["txn_data"]["transaction_type"] == "create"


@pytest.mark.integration
@pytest.mark.costly
def test_scrape_event_list_pages_with_existing_events(config_loader, image_saver):
    load_dotenv(override=True)

    # Setup mock MySQL interface with venue 53
    mock_mysql = MockMySQLInterface()
    mock_mysql.venues = [
        {"id": 53, "name": "Antone's Nightclub", "website_events_url": "https://austinmusiclove.github.io/agro/antonesnightclub_page1.html"}
    ]

    # Add existing events:
    # 1. UPDATE case - event with URL matching first scraped event
    # 2. DELETE case - event with URL not in any scraped event
    mock_mysql.events = [
        {
            "id": 100,
            "venue_id": 53,
            "event_page_url": "https://antonesnightclub.com/tm-event/antones-stage-at-still-austin-monica-valli-single-release/",
            "start_date": "2026-03-13",
            "title": "Old Event Title"
        },
        {
            "id": 200,
            "venue_id": 53,
            "event_page_url": "https://antonesnightclub.com/tm-event/old-event-that-will-be-deleted/",
            "start_date": "2026-04-15",
            "title": "Old Event To Be Deleted"
        }
    ]

    # Create AgroScraper
    fetcher_factory = FetcherFactory(config_loader)
    data_extractor_factory = DataExtractorFactory(config_loader)
    scraper = AgroScraper(fetcher_factory, data_extractor_factory, config_loader)

    # Create EventDataManager
    event_data_manager = EventDataManager(scraper, mock_mysql, image_saver)

    # Execute
    event_data_manager.scrape_event_list_pages(venue_id=53, paginate=True)

    # Assert
    assert len(mock_mysql.get_future_events_calls) > 0, "get_future_events_by_venue should have been called"
    assert len(mock_mysql.saved_transactions) > 0, "save_transaction should have been called"

    # With pagination, we expect 68 events from scrape + 1 delete = 69 total transactions
    # But we have 1 matching (update) + 1 extra existing (delete) + 67 non-matching (create)
    # = 68 create/update + 1 delete = 69 transactions total
    assert len(mock_mysql.saved_transactions) == 69, f"Expected 69 transactions, got {len(mock_mysql.saved_transactions)}"

    # Verify screenshots were saved (should be called 4 times - one per page)
    assert image_saver._save_call_count >= 4, f"Expected 4 screenshot saves, got {image_saver._save_call_count}"

    # Verify we have at least one update transaction
    update_txns = [t for t in mock_mysql.saved_transactions if t["txn_data"]["transaction_type"] == "update"]
    assert len(update_txns) == 1, f"Expected 1 update transaction, got {len(update_txns)}"
    assert update_txns[0]["txn_data"]["current_data_id"] == 100, "Update should reference existing event id 100"

    # Verify we have at least one delete transaction
    delete_txns = [t for t in mock_mysql.saved_transactions if t["txn_data"]["transaction_type"] == "delete"]
    assert len(delete_txns) == 1, f"Expected 1 delete transaction, got {len(delete_txns)}"
    assert delete_txns[0]["txn_data"]["current_data_id"] == 200, "Delete should reference existing event id 200"

    # Verify we have create transactions (remaining scraped events)
    create_txns = [t for t in mock_mysql.saved_transactions if t["txn_data"]["transaction_type"] == "create"]
    assert len(create_txns) == 67, f"Expected 67 create transactions, got {len(create_txns)}"
