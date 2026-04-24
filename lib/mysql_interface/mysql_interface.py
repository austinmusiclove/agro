import os
import pymysql

from lib.mysql_interface.venues import venues
from lib.mysql_interface.events import events
from lib.mysql_interface.staged_transactions import staged_transactions


class MySQLInterface:
    def __init__(self, config_loader):
        mysql_config = config_loader.get_config("agro").get("mysql", {})
        self._host_env = mysql_config.get("host_env", "AGRO_MYSQL_HOST")
        self._port_env = mysql_config.get("port_env", "AGRO_MYSQL_PORT")
        self._user_env = mysql_config.get("user_env", "AGRO_MYSQL_USER")
        self._password_env = mysql_config.get("password_env", "AGRO_MYSQL_PASSWORD")
        self._database_env = mysql_config.get("database_env", "AGRO_MYSQL_DATABASE")

        self.host = os.getenv(self._host_env)
        port_str = os.getenv(self._port_env)
        self.port = int(port_str) if port_str is not None else 3306
        self.user = os.getenv(self._user_env)
        self.password = os.getenv(self._password_env)
        self.database = os.getenv(self._database_env)

        self._connection = None

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

    def connect(self):
        return self._get_connection()

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

    def get_staged_transactions(self, target_table):
        conn = self._get_connection()
        return staged_transactions.get_staged_transactions(conn, target_table)

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
                - current_data_id: ID of existing record (None for create)
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
            if target_table == "events":
                staged_data_id = events.insert_event(conn, data_with_status)

        staged_txn_data = txn_data.copy()
        staged_txn_data["target_table"] = target_table
        staged_txn_data["staged_data_id"] = staged_data_id
        staged_transaction_id = self.insert_staged_transaction(staged_txn_data)

        return {
            "staged_data_id": staged_data_id,
            "staged_transaction_id": staged_transaction_id
        }
