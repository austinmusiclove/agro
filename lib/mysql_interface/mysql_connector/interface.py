from abc import ABC, abstractmethod


class MySQLConnectorInterface(ABC):
    def __init__(self, config_loader=None):
        self._config_loader = config_loader
        self._config = self._load_config()

    def _load_config(self) -> dict:
        if self._config_loader:
            return self._config_loader.get_config("agro").get("mysql", {})
        return {}

    @abstractmethod
    def execute_query(self, sql: str, params: list = None) -> list[dict]:
        pass

    @abstractmethod
    def execute_insert(self, sql: str, params: list = None) -> int:
        pass

    @abstractmethod
    def execute_update(self, sql: str, params: list = None) -> int:
        pass

    @abstractmethod
    def close(self):
        pass
