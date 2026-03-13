import requests

from lib.llm_interface.llm_interface import LlmInterface


class OllamaLlm(LlmInterface):
    def __init__(self, model="phi3"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def _prompt_llm(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        return response

    def get_next_page_url(self, markdown, current_url=None):
        prompt = f"""This is the markdown of a web page that may or may not have pagination. \
            Find the next page link. \
            If found, return only the URL. \
            If not found, return nothing. \
            Markdown: \
            {markdown}"""

        response_text = self._prompt_llm(prompt)

        result = response_text.strip() if response_text else ""
        return self._clean_url(result)

    def get_event_page_urls(self, markdown, current_url=None) -> list[str]:
        pass
