from .interface import ScraperInterface
from .firecrawl_scraper import FirecrawlScraper


class ScraperFactory:
    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._default_implementation = config_loader.get_config("agro").get("scraper", {}).get("default", "firecrawl")

    def create(self, implementation: str = None) -> ScraperInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "firecrawl":
            return FirecrawlScraper()
        else:
            raise ValueError(f"Unknown scraper type requested: {implementation}")
