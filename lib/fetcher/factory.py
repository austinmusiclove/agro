from .interface import FetcherInterface


class FetcherFactory:
    DEFAULT_IMPLEMENTATION = "simple_fetcher"

    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = config_loader.get_config("agro").get("fetcher", {}).get("default", self.DEFAULT_IMPLEMENTATION)

    def create(self, implementation: str = None) -> FetcherInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "simple_fetcher":
            from .simple_fetcher import SimpleFetcher
            return SimpleFetcher()
        elif implementation == "drission_page":
            from .drission_page_fetcher import DrissionPageFetcher
            return DrissionPageFetcher(self._config_loader)
        elif implementation == "playwright":
            from .playwright_fetcher import PlaywrightFetcher
            return PlaywrightFetcher(self._config_loader)
        else:
            raise ValueError(f"Unknown fetcher type requested: {implementation}")
