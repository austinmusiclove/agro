from abc import ABC, abstractmethod

class ScraperInterface(ABC):
    @abstractmethod
    def scrape_event_list_page(self, url: str, paginate: bool = True) -> list[dict]:
        """
        Scrapes a venue's event list page and optionally follows pagination links.
        Returns a list of dictionaries representing the extracted events.
        """
        pass
