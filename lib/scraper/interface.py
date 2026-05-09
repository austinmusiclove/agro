import hashlib
from abc import ABC, abstractmethod


class ScraperInterface(ABC):
    @abstractmethod
    def __init__(self, fetcher_factory, data_extractor_factory, config_loader, image_saver):
        self.fetcher = fetcher_factory.create()
        self.data_extractor = data_extractor_factory.create()
        self.image_saver = image_saver

    @abstractmethod
    def scrape_event_list_page(self, url: str, paginate: bool = True, max_pages: int = 10, venue: dict = None) -> dict:
        """
        Scrapes a venue's event list page and optionally follows pagination links.
        Returns a dict with 'events' (list of dicts) and 'screenshots' (list of refs or None).
        """
        pass

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Computes SHA256 hash of content. Returns None if content is None or empty."""
        if not content:
            return None
        return hashlib.sha256(content.encode()).hexdigest()
