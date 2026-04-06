from .interface import ScraperInterface
from .firecrawl_scraper import FirecrawlScraper
from .agro_scraper import AgroScraper


class ScraperFactory:
    def __init__(self, config_loader, fetcher_factory=None, data_extractor_factory=None):
        self._config_loader = config_loader
        self._fetcher_factory = fetcher_factory
        self._data_extractor_factory = data_extractor_factory
        self._default_implementation = config_loader.get_config("agro").get("scraper", {}).get("default", "firecrawl")

    def create(self, implementation: str = None) -> ScraperInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "firecrawl":
            return FirecrawlScraper()
        elif implementation == "agro":
            if not self._fetcher_factory or not self._data_extractor_factory:
                raise ValueError("AgroScraper requires fetcher_factory and data_extractor_factory")
            return AgroScraper(self._fetcher_factory, self._data_extractor_factory, self._config_loader)
        else:
            raise ValueError(f"Unknown scraper type requested: {implementation}")
