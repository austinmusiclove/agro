from abc import ABC, abstractmethod


class LlmInterface(ABC):
    @abstractmethod
    def _prompt_llm(self, prompt):
        """Override this in subclasses to implement actual LLM call."""
        pass

    def get_next_page_url(self, markdown):
        prompt = f"""Find the next page link in this markdown.
Return only the URL if found, or return nothing if there is no next page.
Markdown:
{markdown}"""

        result = self._prompt_llm(prompt).strip()
        return self._clean_url(result)

    def _clean_url(self, url):
        """Validate and clean a URL. Returns cleaned URL or None if invalid."""
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        return None
