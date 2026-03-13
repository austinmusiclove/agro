import os
import json
from pydantic import BaseModel, Field
from urllib.parse import urljoin
from google import genai
from google.genai import types

from lib.llm_interface.llm_interface import LlmInterface


class NextPageResult(BaseModel):
    next_url: str = Field(
        description="The exact URL or relative path to the next page of results. Return an empty string '' if no next page link is found."
    )


class GeminiLlm(LlmInterface):
    def __init__(self, model="gemini-2.5-flash"):
        self.model = model
        # The client automatically picks up the GEMINI_API_KEY environment variable.
        self.client = genai.Client()

    def _prompt_llm(self, prompt):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text

    def _prompt_llm_structured_output(self, prompt, response_schema=None):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            },
        )
        return response.text

    def get_next_page_url(self, markdown, current_url=None):

        prompt = f"""You are an automated data extraction system. Your sole purpose is to parse HTML/Markdown and extract specific links. You MUST output strictly in the requested JSON format. You do not explain, you do not converse.
Find the link to the next page of results (e.g., "Next", ">").
Extract the *exact* URL or path found in the markdown link.
If no next page link is found, return an empty string.

<MARKDOWN_DATA>
{markdown}
</MARKDOWN_DATA>"""

        response_text = self._prompt_llm_structured_output(
            prompt,
            response_schema=NextPageResult,
        )

        try:
            data = json.loads(response_text)
            result = data.get("next_url")
            # Convert empty string back to None to match expectations
            if result == "":
                result = None
        except (json.JSONDecodeError, TypeError):
            print("Error: Failed to parse JSON response from LLM.")
            result = None

        if result and current_url:
            result = urljoin(current_url, result)

        return self._clean_url(result)
