import os
import json
from urllib.parse import urljoin
from google import genai
from google.genai import types

from lib.llm_interface.llm_interface import LlmInterface


class GeminiLlm(LlmInterface):
    def __init__(self, model="gemini-2.5-flash"):
        self.model = model
        # The client automatically picks up the GEMINI_API_KEY environment variable.
        self.client = genai.Client()

    def _prompt_llm(self, prompt, expect_json=False):
        config = types.GenerateContentConfig(
            response_mime_type="application/json"
        ) if expect_json else None

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

    def get_next_page_url(self, markdown, current_url=None):
        prompt = f"""You are a strict data extractor. Analyze the following markdown of a web page and find the link to the next page of results (e.g., pagination "Next", ">", "Next Page", etc.). \
            Return ONLY a JSON object with a single key "next_page_link". \
            If you find a next page link, set the value to the exact link found in the markdown. Do not guess or invent links. \
            The link may be just a path instead of a full URL. \
            If you cannot find a next page link, set the value to null. \
            Markdown: \
            {markdown}"""

        print("Extracting next page URL...")
        response_text = self._prompt_llm(prompt, expect_json=True)
        print(f"LLM Response: {response_text}")

        try:
            data = json.loads(response_text)
            result = data.get("next_page_link")
        except (json.JSONDecodeError, TypeError):
            print("Error: Failed to parse JSON response from LLM.")
            result = None

        if result and current_url:
            result = urljoin(current_url, result)

        return self._clean_url(result)
