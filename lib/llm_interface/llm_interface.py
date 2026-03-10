from abc import ABC, abstractmethod


class LlmInterface(ABC):
    @abstractmethod
    def _prompt_llm(self, prompt):
        """Override this in subclasses to implement actual LLM call."""
        pass

    def get_next_page_url(self, markdown):
        prompt = f"""This is the markdown of a web page that may or may not have pagination.
Find the next page link.
If found, return only the URL.
If not found, return nothing.
Markdown:
{markdown}"""

        print(prompt)
        response = self._prompt_llm(prompt)
        print(response)
        result = response.strip() if response else ""
        return self._clean_url(result)

    def _clean_url(self, url):
        """Validate and clean a URL. Returns cleaned URL or None if invalid."""
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        return None
