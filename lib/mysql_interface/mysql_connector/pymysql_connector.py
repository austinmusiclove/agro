import os
import pymysql
from pymysql.cursors import DictCursor

from .interface import MySQLConnectorInterface


class PyMySQLConnector(MySQLConnectorInterface):
    def __init__(self, config_loader):
        super().__init__(config_loader)
        self.host = self._config.get("host", "localhost")
        port_val = self._config.get("port", 3306)
        self.port = int(port_val) if port_val is not None else 3306
        self.user = self._config.get("user", "root")
        self.database = self._config.get("database", "agro")
        self._password_env = self._config.get("password_env", "AGRO_MYSQL_PASSWORD")
        self.password = os.getenv(self._password_env)
        self._connection = None

    def _get_connection(self):
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor
            )
        return self._connection

    def _convert_placeholders(self, sql: str) -> str:
        return sql.replace("?", "%s")

    def execute_query(self, sql: str, params: list = None) -> list[dict]:
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(self._convert_placeholders(sql), params or [])
            return cursor.fetchall()

    def execute_insert(self, sql: str, params: list = None) -> int:
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(self._convert_placeholders(sql), params or [])
            conn.commit()
            return cursor.lastrowid

    def execute_update(self, sql: str, params: list = None) -> int:
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(self._convert_placeholders(sql), params or [])
            conn.commit()
            return cursor.rowcount

    def close(self):
        if self._connection and self._connection.open:
            self._connection.close()
