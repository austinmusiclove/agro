from abc import ABC, abstractmethod


class DataExtractorInterface(ABC):
    @abstractmethod
    def extract_event_list(self, markdown: str) -> dict:
        """
        Extracts a list of events from markdown content.
        Returns a dictionary containing the list of events and optional next page URL.
        """
        pass

    @abstractmethod
    def extract_event(self, markdown: str) -> dict:
        """
        Extracts a single event from markdown content.
        Returns a dictionary representing the extracted event.
        """
        pass
