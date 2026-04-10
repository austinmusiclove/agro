import os
import json
import pymysql

from lib.mysql_interface.venues import venues
from lib.mysql_interface.events import events
from lib.mysql_interface.staged_transactions import staged_transactions


class MySQLInterface:
    def __init__(self):
        self.host = os.environ.get("AGRO_MYSQL_HOST")
        self.port = os.environ.get("AGRO_MYSQL_PORT")
        self.user = os.environ.get("AGRO_MYSQL_USER")
        self.password = os.environ.get("AGRO_MYSQL_PASSWORD")
        self.database = os.environ.get("AGRO_MYSQL_DATABASE")

        self._validate_env_vars()
        self._connection = None

    def _validate_env_vars(self):
        missing = []
        if not self.host:
            missing.append("AGRO_MYSQL_HOST")
        if not self.port:
            missing.append("AGRO_MYSQL_PORT")
        if not self.user:
            missing.append("AGRO_MYSQL_USER")
        if not self.password:
            missing.append("AGRO_MYSQL_PASSWORD")
        if not self.database:
            missing.append("AGRO_MYSQL_DATABASE")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        self.port = int(self.port)

    def _get_connection(self):
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor
            )
        return self._connection

    def close(self):
        if self._connection and self._connection.open:
            self._connection.close()

    def get_venue_by_id(self, venue_id):
        conn = self._get_connection()
        return venues.get_venue_by_id(conn, venue_id)

    def get_all_venues(self):
        conn = self._get_connection()
        return venues.get_all_venues(conn)

    def get_future_events_by_venue(self, venue_id):
        conn = self._get_connection()
        return events.get_future_events_by_venue(conn, venue_id)

    def insert_event(self, event_data):
        conn = self._get_connection()
        return events.insert_event(conn, event_data)

    def insert_staged_transaction(self, transaction_data):
        conn = self._get_connection()
        return staged_transactions.insert_staged_transaction(conn, transaction_data)

    def stage_transaction(self, target_table: str, data: dict, txn_data: dict) -> dict:
        """
        Saves a staged record to the target table and creates a staged_transaction record for manual review.

        Args:
            target_table: Name of the table to insert the staged record into
            data: Dict of column names and values to insert
            txn_data: Dict containing:
                - transaction_type: 'create', 'update', or 'delete'
                - current_data_row_id: ID of existing record (None for create)
                - data_index: Optional index that denotes the position of this data item in the screenshot. This is meant to assist with manual review
                - screenshot: Optional screenshot reference
                - schema_blob: Optional dict
                - scrape_url: URL that was scraped

        Returns:
            Dict with 'staged_data_id' and 'staged_transaction_id'
        """
        conn = self._get_connection()

        staged_data_id = None
        data_with_status = data.copy()
        data_with_status["status"] = "staged"
        txn_type = txn_data.get("transaction_type")
        if txn_type == "create" or txn_type == "update":
            match target_table:
                case "events":
                    staged_data_id = insert_event(self, data_with_status):
                    print("Success")
                case _:  # Wildcard (Default case)
                    print("Unknown target_table when trying to insert staged data")

        staged_txn_data = txn_data.copy()
        staged_txn_data["target_table"] = target_table
        staged_txn_data["staged_data_id"] = staged_data_id
        staged_transaction_id = self.insert_staged_transaction(staged_txn_data)

        return {
            "staged_data_id": staged_data_id,
            "staged_transaction_id": staged_transaction_id
        }
