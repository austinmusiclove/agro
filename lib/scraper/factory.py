import os
from .interface import ScraperInterface
from .firecrawl_scraper import FirecrawlScraper

class ScraperFactory:
    @staticmethod
    def get_scraper() -> ScraperInterface:
        scraper_type = os.getenv("AGRO_SCRAPER", "firecrawl").lower()
        
        if scraper_type == "firecrawl":
            return FirecrawlScraper()
        else:
            raise ValueError(f"Unknown scraper type requested: {scraper_type}")
