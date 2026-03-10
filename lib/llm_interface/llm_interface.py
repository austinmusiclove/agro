import json
from abc import ABC, abstractmethod
from urllib.parse import urljoin


class LlmInterface(ABC):
    @abstractmethod
    def _prompt_llm(self, prompt, expect_json=False):
        """Override this in subclasses to implement actual LLM call."""
        pass

    def get_next_page_url(self, markdown, current_url=None):
        prompt = f"""You are a strict data extractor. Analyze the following markdown of a web page and find the link to the next page of results (e.g., pagination "Next", ">", "Page 2", etc.).
Return ONLY a JSON object with a single key "next_url".
If you find a next page link, set the value to the exact URL found in the markdown. Do not guess or invent URLs.
If you cannot find a next page link, set the value to null.
Markdown:
{markdown}"""

        print("Extracting next page URL...")
        response_text = self._prompt_llm(prompt, expect_json=True)
        print(f"LLM Response: {response_text}")
        
        try:
            data = json.loads(response_text)
            result = data.get("next_url")
        except (json.JSONDecodeError, TypeError):
            print("Error: Failed to parse JSON response from LLM.")
            result = None

        if result and current_url:
            result = urljoin(current_url, result)

        return self._clean_url(result)

    def _clean_url(self, url):
        """Validate and clean a URL. Returns cleaned URL or None if invalid."""
        if url and (url.startswith("http://") or url.startswith("https://")):
            return url
        return None