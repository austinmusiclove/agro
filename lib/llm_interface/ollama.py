import requests

from lib.llm_interface.llm_interface import LlmInterface


class OllamaLlm(LlmInterface):
    def __init__(self, model="phi3"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def _prompt_llm(self, prompt, expect_json=False):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if expect_json:
            payload["format"] = "json"

        response = requests.post(self.url, json=payload)
        return response.json().get("response", "")

    def get_next_page_url(self, markdown, current_url=None):
        prompt = f"""This is the markdown of a web page that may or may not have pagination. \
            Find the next page link. \
            If found, return only the URL. \
            If not found, return nothing. \
            Markdown: \
            {markdown}"""

        print("Extracting next page URL...")
        response_text = self._prompt_llm(prompt, expect_json=False)
        print(f"LLM Response: {response_text}")

        result = response_text.strip() if response_text else ""
        return self._clean_url(result)
