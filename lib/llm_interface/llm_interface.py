from abc import ABC, abstractmethod


class LlmInterface(ABC):
    @abstractmethod
    def get_next_page_url(self, markdown):
        pass

    def _clean_url(self, url):
        """Validate and clean a URL. Returns cleaned URL or None if invalid."""
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        return None
