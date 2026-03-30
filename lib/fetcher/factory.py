from .interface import FetcherInterface
from .simple_fetcher import SimpleFetcher
from .drission_page_fetcher import DrissionPageFetcher


class FetcherFactory:
    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = config_loader.get_config("agro").get("fetcher", {}).get("default", "simple")

    def create(self, implementation: str = None) -> FetcherInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "simple":
            return SimpleFetcher()
        elif implementation == "drission_page":
            return DrissionPageFetcher()
        else:
            raise ValueError(f"Unknown fetcher type requested: {implementation}")
