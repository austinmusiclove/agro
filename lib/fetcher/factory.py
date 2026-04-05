from .interface import FetcherInterface
from .simple_fetcher import SimpleFetcher
from .drission_page_fetcher import DrissionPageFetcher


class FetcherFactory:
    DEFAULT_IMPLEMENTATION = "simple_fetcher"

    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = config_loader.get_config("agro").get("fetcher", {}).get("default", self.DEFAULT_IMPLEMENTATION)

    def create(self, implementation: str = None) -> FetcherInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "simple_fetcher":
            return SimpleFetcher()
        elif implementation == "drission_page":
            return DrissionPageFetcher(self._config_loader)
        else:
            raise ValueError(f"Unknown fetcher type requested: {implementation}")
