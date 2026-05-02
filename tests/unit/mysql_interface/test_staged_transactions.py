import pytest
from dotenv import load_dotenv

from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.scraper.interface import ScraperInterface
from lib.config.yaml_config_loader import YamlConfigLoader

load_dotenv(override=True)


@pytest.fixture
def db():
    config_loader = YamlConfigLoader()
    mysql_connector_factory = MySQLConnectorFactory(config_loader)
    mysql_connector = mysql_connector_factory.create()
    interface = MySQLInterface(config_loader, mysql_connector)
    yield interface
    interface.close()


class TestInsertStagedTransaction:
    def test_insert_with_hash_fields(self, db):
        html_hash = ScraperInterface._compute_hash("<html><body>test event html</body></html>")
        markdown_hash = ScraperInterface._compute_hash("## Test Event\nSome markdown content")

        transaction_data = {
            "target_table": "events",
            "current_data_id": 1,
            "staged_data_id": None,
            "transaction_type": "create",
            "data_index": 0,
            "screenshot": None,
            "scrape_url": "https://example.com/test",
            "scrape_html_hash": html_hash,
            "scrape_markdown_hash": markdown_hash,
        }

        inserted_id = db.insert_staged_transaction(transaction_data)

        try:
            record = db.get_staged_transaction_with_data(inserted_id)

            assert record is not None
            assert record["scrape_html_hash"] == html_hash
            assert record["scrape_markdown_hash"] == markdown_hash
            assert record["target_table"] == "events"
            assert record["scrape_url"] == "https://example.com/test"
        finally:
            db.execute_update("DELETE FROM staged_transactions WHERE id = ?", [inserted_id])
