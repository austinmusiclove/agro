import json
import logging
import pytest
from dotenv import load_dotenv

from lib.mysql_interface.events import events
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.staged_transactions import insert_staged_transaction
from lib.lambdas.staged_transactions import approve_transaction
from lib.config.yaml_config_loader import YamlConfigLoader

load_dotenv(override=True)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@pytest.fixture
def connector():
    config_loader = YamlConfigLoader()
    mysql_connector_factory = MySQLConnectorFactory(config_loader)
    connector = mysql_connector_factory.create()
    yield connector
    connector.close()


@pytest.fixture
def mysql_interface(connector):
    config_loader = YamlConfigLoader()
    return MySQLInterface(config_loader, connector)


class TestInsertEvent:
    def test_title_with_apostrophe_not_escaped(self, connector):
        event_data = {
            "title": "Antone's Stage: Monica Valli (Single Release)",
            "venue_id": 1,
            "start_date": "2026-06-01",
            "start_time": "20:00:00",
            "status": "staged",
            "event_page_url": "https://example.com/test",
            "ticket_url": "https://example.com/tickets",
        }

        inserted_id = events.insert_event(connector, event_data)

        try:
            event = events.get_event_by_id(connector, inserted_id)

            assert event is not None
            assert "Antone\\'s" not in event["title"], "Apostrophe was backslash-escaped"
            assert event["title"] == "Antone's Stage: Monica Valli (Single Release)"
        finally:
            connector.execute_update("DELETE FROM events WHERE id = ?", [inserted_id])


class TestApproveTransaction:
    def test_approve_create_apostrophe_not_escaped(self, connector, mysql_interface):
        event_data = {
            "title": "Antone's Stage: Monica Valli (Single Release)",
            "venue_id": 1,
            "start_date": "2026-06-01",
            "start_time": "20:00:00",
            "status": "staged",
            "event_page_url": "https://example.com/test",
            "ticket_url": "https://example.com/tickets",
        }

        staged_event_id = events.insert_event(connector, event_data)

        txn_data = {
            "target_table": "events",
            "current_data_id": None,
            "staged_data_id": staged_event_id,
            "transaction_type": "create",
            "data_index": None,
            "screenshot": None,
            "scrape_url": "https://example.com/test",
            "scrape_html_hash": None,
            "scrape_markdown_hash": None,
        }

        staged_txn_id = insert_staged_transaction(connector, txn_data)

        published_event_id = None
        try:
            response = approve_transaction.approve_transaction(mysql_interface, logger, staged_txn_id)

            assert response["statusCode"] == 200

            body = json.loads(response["body"])
            published_event_id = body["event_id"]

            published_event = events.get_event_by_id(connector, published_event_id)

            assert published_event is not None
            assert "Antone\\'s" not in published_event["title"], "Apostrophe was backslash-escaped during approval"
            assert published_event["title"] == "Antone's Stage: Monica Valli (Single Release)"
        finally:
            connector.execute_update("DELETE FROM events WHERE id IN (?, ?)", [staged_event_id, published_event_id])
            connector.execute_update("DELETE FROM staged_transactions WHERE id = ?", [staged_txn_id])
