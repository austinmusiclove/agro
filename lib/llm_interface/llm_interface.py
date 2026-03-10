from abc import ABC, abstractmethod


class LlmInterface(ABC):
    @abstractmethod
    def _prompt_llm(self, prompt, expect_json=False):
        """Override this in subclasses to implement actual LLM call."""
        pass

    def get_next_page_url(self, markdown, current_url=None):
        """Override this in subclasses to implement finding the next page link in a webpage markdown"""
        pass

    def _clean_url(self, url):
        """Validate and clean a URL. Returns cleaned URL or None if invalid."""
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        return None
