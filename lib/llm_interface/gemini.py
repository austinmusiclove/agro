import os
import json
from typing import Optional
from pydantic import BaseModel, Field
from urllib.parse import urljoin
from google import genai
from google.genai import types

from lib.llm_interface.llm_interface import LlmInterface


class NextPageResult(BaseModel):
    next_url: str = Field(
        description="The exact URL or relative path to the next page of results. Return an empty string '' if no next page link is found."
    )


class EventUrlsResult(BaseModel):
    event_urls: list[str] = Field(
        description="A list of exact URLs or relative paths to individual live music event pages. Return an empty list if none are found."
    )


class GeminiLlm(LlmInterface):
    def __init__(self, model="gemini-1.5-pro"):
        self.model = model
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def _prompt_llm(self, prompt) -> Optional[str]:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text

    def _prompt_llm_structured_output(self, prompt, response_schema=None) -> Optional[str]:

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

    def get_next_page_url(self, markdown, current_url=None) -> Optional[str]:

        prompt = f"""You are an automated data extraction system. Your sole purpose is to parse HTML/Markdown and extract specific links. You MUST output strictly in the requested JSON format. You do not explain, you do not converse.
Find the link to the next page of results (e.g., "Next", ">").
Extract the *exact* URL or path found in the markdown link.
If no next page link is found, return an empty string.

<MARKDOWN_DATA>
{markdown}
</MARKMOD_DATA>"""

        response_text = self._prompt_llm_structured_output(
            prompt,
            response_schema=NextPageResult,
        )

        try:
            if response_text is None:
                data = {}
            else:
                data = json.loads(response_text)
            result = data.get("next_url")
            if result == "":
                result = None
        except (json.JSONDecodeError, TypeError):
            print("Error: Failed to parse JSON response from LLM.")
            result = None

        if result and current_url:
            result = urljoin(current_url, result)

        return self._clean_url(result)

    def get_event_page_urls(self, markdown, current_url=None) -> list[str]:
        prompt = f"""You are an automated data extraction system. Your sole purpose is to parse HTML/Markdown and extract specific links. You MUST output strictly in the requested JSON format. You do not explain, you do not converse.
From the following markdown, identify and extract URLs that lead to *individual live music event pages*.
Exclude links for general venue information, contact pages, menus, social media, or other non-event-specific pages.
If no live music event URLs are found, return an empty list.

<MARKDOWN_DATA>
{markdown}
</MARKDOWN_DATA>"""

        response_text = self._prompt_llm_structured_output(
            prompt,
            response_schema=EventUrlsResult,
        )
        print(response_text)

        try:
            if response_text is None:
                data = {}
            else:
                data = json.loads(response_text)
            raw_urls = data.get("event_urls", [])
        except (json.JSONDecodeError, TypeError):
            print("Error: Failed to parse JSON response from LLM.")
            raw_urls = []

        cleaned_urls = []
        print(raw_urls)
        for url in raw_urls:
            if current_url:
                url = urljoin(current_url, url)
            cleaned_url = self._clean_url(url)
            if cleaned_url:
                cleaned_urls.append(cleaned_url)

        print(cleaned_urls)
        return cleaned_urls
