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
