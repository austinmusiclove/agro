import os
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
