import os
import pymysql


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
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM venues WHERE id = %s", (venue_id,))
            return cursor.fetchone()

    def get_all_venues(self):
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM venues")
            return cursor.fetchall()

    def get_events_by_venue(self, venue_id):
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM events WHERE venue_id = %s AND date > NOW()",
                (venue_id,)
            )
            return cursor.fetchall()
