from lib.mysql_interface.venues import venues
from lib.mysql_interface.events import events
from lib.mysql_interface.staged_transactions import staged_transactions


class MySQLInterface:
    def __init__(self, config_loader, mysql_connector):
        self._config_loader = config_loader
        self._connector = mysql_connector

    def close(self):
        self._connector.close()

    def execute_query(self, sql: str, params: list = None) -> list[dict]:
        return self._connector.execute_query(sql, params)

    def execute_insert(self, sql: str, params: list = None) -> int:
        return self._connector.execute_insert(sql, params)

    def execute_update(self, sql: str, params: list = None) -> int:
        return self._connector.execute_update(sql, params)

    def get_venue_by_id(self, venue_id):
        return venues.get_venue_by_id(self._connector, venue_id)

    def get_all_venues(self):
        return venues.get_all_venues(self._connector)

    def get_future_events_by_venue(self, venue_id):
        return events.get_future_events_by_venue(self._connector, venue_id)

    def get_event_by_id(self, event_id):
        return events.get_event_by_id(self._connector, event_id)

    def insert_event(self, event_data):
        return events.insert_event(self._connector, event_data)

    def get_staged_transactions(self, target_table):
        return staged_transactions.get_staged_transactions(self._connector, target_table)

    def get_staged_transaction_with_data(self, transaction_id):
        return staged_transactions.get_staged_transaction_with_data(self._connector, transaction_id)

    def insert_staged_transaction(self, transaction_data):
        return staged_transactions.insert_staged_transaction(self._connector, transaction_data)

    def update_staged_transaction(self, transaction_id: int, updates: dict):
        return staged_transactions.update_staged_transaction(self._connector, transaction_id, updates)

    def stage_transaction(self, target_table: str, data: dict, txn_data: dict) -> dict:
        return staged_transactions.stage_transaction(self._connector, target_table, data, txn_data)
