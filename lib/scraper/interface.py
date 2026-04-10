import hashlib
from abc import ABC, abstractmethod


class ScraperInterface(ABC):
    @abstractmethod
    def scrape_event_list_page(self, url: str, paginate: bool = True, max_pages: int = 10) -> dict:
        """
        Scrapes a venue's event list page and optionally follows pagination links.
        Returns a dict with 'events' (list of dicts) and 'screenshots' (list of bytes).
        """
        pass

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Computes SHA256 hash of content. Returns None if content is None or empty."""
        if not content:
            return None
        return hashlib.sha256(content.encode()).hexdigest()
