import pytest
from unittest.mock import MagicMock
from lib.event_data_manager.event_data_manager import EventDataManager
from tests.mocks.mock_mysql_interface import MockMySQLInterface


def create_manager(existing_events=None):
    mock_db = MockMySQLInterface()
    if existing_events is not None:
        mock_db.events = existing_events

    scraper = MagicMock()
    manager = EventDataManager(scraper, mock_db)
    return manager


class TestMergeEvents:
    def test_no_existing_events_all_create(self):
        manager = create_manager(existing_events=[])
        scraped = [
            {"event_page_url": "http://example.com/1", "title": "Event 1", "start_date": "2026-01-01"},
            {"event_page_url": "http://example.com/2", "title": "Event 2", "start_date": "2026-01-02"},
        ]

        result = manager._merge_events([], scraped)

        assert len(result) == 2
        assert all(t["transaction_type"] == "create" for t in result)
        assert all(t["existing_event_id"] is None for t in result)

    def test_no_scraped_events_all_delete(self):
        manager = create_manager(existing_events=[
            {"id": 1, "event_page_url": "http://example.com/1", "title": "Event 1", "start_date": "2026-01-01", "status": "published"},
            {"id": 2, "event_page_url": "http://example.com/2", "title": "Event 2", "start_date": "2026-01-02", "status": "published"},
        ])

        result = manager._merge_events(manager.mysql_interface.events, [])

        assert len(result) == 2
        assert all(r["transaction_type"] == "delete" for r in result)
        assert result[0]["existing_event_id"] == 1
        assert result[1]["existing_event_id"] == 2

    def test_match_by_url_returns_update(self):
        manager = create_manager(existing_events=[
            {"id": 1, "event_page_url": "http://example.com/1", "title": "Old Title", "start_date": "2026-01-01", "status": "published"},
        ])
        scraped = [
            {"event_page_url": "http://example.com/1", "title": "New Title", "start_date": "2026-01-01"},
        ]

        result = manager._merge_events(manager.mysql_interface.events, scraped)

        assert len(result) == 1
        assert result[0]["transaction_type"] == "update"
        assert result[0]["existing_event_id"] == 1

    def test_match_by_date_returns_update(self):
        manager = create_manager(existing_events=[
            {"id": 1, "event_page_url": None, "title": "Old Title", "start_date": "2026-01-01", "status": "published"},
        ])
        scraped = [
            {"event_page_url": None, "title": "New Title", "start_date": "2026-01-01"},
        ]

        result = manager._merge_events(manager.mysql_interface.events, scraped)

        assert len(result) == 1
        assert result[0]["transaction_type"] == "update"
        assert result[0]["existing_event_id"] == 1

    def test_mixed_create_update_delete(self):
        manager = create_manager(existing_events=[
            {"id": 1, "event_page_url": "http://example.com/1", "title": "Event 1", "start_date": "2026-01-01", "status": "published"},
            {"id": 2, "event_page_url": "http://example.com/2", "title": "Event 2", "start_date": "2026-01-02", "status": "published"},
            {"id": 3, "event_page_url": "http://example.com/old", "title": "Old Event", "start_date": "2026-01-03", "status": "published"},
        ])
        existing = manager.mysql_interface.events
        scraped = [
            {"event_page_url": "http://example.com/1", "title": "Updated Event 1", "start_date": "2026-01-01"},
            {"event_page_url": "http://example.com/2", "title": "Event 2", "start_date": "2026-01-02"},
            {"event_page_url": "http://example.com/new", "title": "New Event", "start_date": "2026-01-04"},
        ]

        result = manager._merge_events(existing, scraped)

        assert len(result) == 4

        update_txns = [t for t in result if t["transaction_type"] == "update"]
        assert len(update_txns) == 2

        create_txns = [t for t in result if t["transaction_type"] == "create"]
        assert len(create_txns) == 1

        delete_txns = [t for t in result if t["transaction_type"] == "delete"]
        assert len(delete_txns) == 1
        assert delete_txns[0]["existing_event_id"] == 3

    def test_event_without_url_or_date_creates(self):
        manager = create_manager(existing_events=[])
        scraped = [
            {"title": "Event with no date or URL"},
        ]

        result = manager._merge_events([], scraped)

        assert len(result) == 1
        assert result[0]["transaction_type"] == "create"

    def test_prefers_url_over_date_matching(self):
        manager = create_manager(existing_events=[
            {"id": 1, "event_page_url": "http://example.com/1", "title": "By URL", "start_date": "2026-01-01", "status": "published"},
            {"id": 2, "event_page_url": None, "title": "By Date", "start_date": "2026-01-01", "status": "published"},
        ])
        existing = manager.mysql_interface.events
        scraped = [
            {"event_page_url": "http://example.com/1", "title": "Matched by URL", "start_date": "2026-01-01"},
        ]

        result = manager._merge_events(existing, scraped)

        assert len(result) == 2
        update_txn = next(t for t in result if t["transaction_type"] == "update")
        assert update_txn["existing_event_id"] == 1

        delete_txn = next(t for t in result if t["transaction_type"] == "delete")
        assert delete_txn["existing_event_id"] == 2

    def test_empty_lists_returns_empty_transactions(self):
        manager = create_manager(existing_events=[])

        result = manager._merge_events([], [])

        assert result == []

    def test_preserves_scraped_event_data_in_create(self):
        manager = create_manager(existing_events=[])
        scraped = [
            {"event_page_url": "http://example.com/1", "title": "Test Event", "start_date": "2026-01-01", "price": "$10"},
        ]

        result = manager._merge_events([], scraped)

        assert result[0]["event_data"]["title"] == "Test Event"
        assert result[0]["event_data"]["price"] == "$10"

    def test_preserves_scraped_event_data_in_update(self):
        manager = create_manager(existing_events=[
            {"id": 1, "event_page_url": "http://example.com/1", "title": "Old", "start_date": "2026-01-01", "status": "published"},
        ])
        scraped = [
            {"event_page_url": "http://example.com/1", "title": "New", "start_date": "2026-01-01", "price": "$20"},
        ]

        result = manager._merge_events(manager.mysql_interface.events, scraped)

        assert result[0]["transaction_type"] == "update"
        assert result[0]["event_data"]["title"] == "New"
        assert result[0]["event_data"]["price"] == "$20"
