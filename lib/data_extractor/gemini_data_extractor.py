import os
import time
import json
from google import genai
from google.genai import types
from google.api_core.exceptions import TooManyRequests, DeadlineExceeded, ServiceUnavailable

from lib.schemas.event import Event
from lib.schemas.event_list import EventList
from lib.data_extractor.interface import DataExtractorInterface


class GeminiDataExtractor(DataExtractorInterface):
    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._load_config()

        self._last_request_time = 0

    def _load_config(self) -> None:
        config = self._config_loader.get_config("gemini")

        self.model = config.get("gemini", {}).get("model", "gemini-2.5-flash")
        api_key_env = config.get("gemini", {}).get("api_key_env", "GEMINI_API_KEY")

        self.client = genai.Client(api_key=os.getenv(api_key_env))

        retry_config = config.get("gemini", {}).get("retry", {})
        self.max_attempts = retry_config.get("max_attempts", 3)
        self.initial_delay = retry_config.get("initial_delay", 1)
        self.max_delay = retry_config.get("max_delay", 30)
        self.exponential_base = retry_config.get("exponential_base", 2)

        self.rate_limit_delay = config.get("gemini", {}).get("rate_limit_delay", 0.5)

    def _call_gemini(self, system_prompt: str, user_prompt: str, response_schema):
        self._apply_rate_limit()

        retry_decorator = self._get_retry_decorator((TooManyRequests, DeadlineExceeded, ServiceUnavailable))
        decorated_func = retry_decorator(self._make_api_call)
        return decorated_func(system_prompt, user_prompt, response_schema)

    def _make_api_call(self, system_prompt: str, user_prompt: str, response_schema):
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=config,
        )
        return response

    def _parse_response(self, response_text: str, schema_class):
        data = json.loads(response_text)
        instance = schema_class(**data)
        instance.clean()
        return instance

    def extract_event_list(self, markdown: str) -> dict:
        system_prompt = """You are an expert at extracting structured event data from markdown content.
Extract the events into the specified JSON schema format. All URLs must be absolute (start with http:// or https://). Never return relative paths."""

        user_prompt = f"""Extract the list of events from the markdown content, as well as the link to the next page of events if one exists. Make sure to get every event. Do not skip events.

Markdown content:
{markdown}"""

        response = self._call_gemini(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=EventList
        )

        event_list = self._parse_response(response.text, EventList)
        return event_list.model_dump()

    def extract_event(self, markdown: str) -> dict:
        system_prompt = """You are an expert at extracting structured event data from markdown content.
Extract the event into the specified JSON schema format. All URLs must be absolute (start with http:// or https://). Never return relative paths."""

        user_prompt = f"""Extract a single event from this markdown content.
Return the data in the Event schema format.

Markdown content:
{markdown}"""

        response = self._call_gemini(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_schema=Event
        )

        event = self._parse_response(response.text, Event)
        return event.model_dump()
