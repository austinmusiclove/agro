from lib.mysql_interface.mysql_connector.interface import MySQLConnectorInterface


class MockConnector(MySQLConnectorInterface):
    def __init__(self, config_loader=None):
        super().__init__(config_loader)
        self.queries = []
        self.inserts = []
        self.updates = []

    def execute_query(self, sql: str, params: list = None) -> list[dict]:
        self.queries.append({"sql": sql, "params": params})
        return []

    def execute_insert(self, sql: str, params: list = None) -> int:
        self.inserts.append({"sql": sql, "params": params})
        return 1

    def execute_update(self, sql: str, params: list = None) -> int:
        self.updates.append({"sql": sql, "params": params})
        return 1

    def close(self):
        pass
