from .interface import MySQLConnectorInterface


class MySQLConnectorFactory:
    DEFAULT_IMPLEMENTATION = "pymysql"

    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = (
            config_loader.get_config("agro")
            .get("mysql_connector", {})
            .get("default", self.DEFAULT_IMPLEMENTATION)
        )

    def create(self, implementation: str = None) -> MySQLConnectorInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "pymysql":
            from .pymysql_connector import PyMySQLConnector
            return PyMySQLConnector(self._config_loader)
        elif implementation == "boto":
            from .boto_connector import BotoConnector
            return BotoConnector(self._config_loader)
        else:
            raise ValueError(f"Unknown mysql_connector type: {implementation}")
