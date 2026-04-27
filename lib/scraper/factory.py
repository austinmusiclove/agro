from .interface import ScraperInterface


class ScraperFactory:
    def __init__(self, config_loader, fetcher_factory=None, data_extractor_factory=None):
        self._config_loader = config_loader
        self._fetcher_factory = fetcher_factory
        self._data_extractor_factory = data_extractor_factory
        print('scraper config')
        print(config_loader.get_config("agro").get("scraper", {}).get("default", "default_imp"))
        self._default_implementation = config_loader.get_config("agro").get("scraper", {}).get("default", "agro")
        print(self._default_implementation)

    def create(self, implementation: str = None) -> ScraperInterface:
        if implementation is None:
            implementation = self._default_implementation

        if implementation == "firecrawl":
            pass
            from .firecrawl_scraper import FirecrawlScraper
            return FirecrawlScraper()
        elif implementation == "agro":
            if not self._fetcher_factory or not self._data_extractor_factory:
                raise ValueError("AgroScraper requires fetcher_factory and data_extractor_factory")
            from .agro_scraper import AgroScraper
            return AgroScraper(self._fetcher_factory, self._data_extractor_factory, self._config_loader)
        else:
            raise ValueError(f"Unknown scraper type requested: {implementation}")
