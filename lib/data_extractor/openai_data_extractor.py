import os
import time
from openai import OpenAI, APIError, RateLimitError, Timeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from lib.schemas.event import Event
from lib.schemas.event_list import EventListSchema
from lib.data_extractor.interface import DataExtractorInterface


class OpenAiDataExtractor(DataExtractorInterface):
    def __init__(self, config_loader):
        self._config_loader = config_loader
        self._load_config()

        self._last_request_time = 0

    def _load_config(self) -> None:
        config = self._config_loader.get_config("openai")

        self.model = config.get("openai", {}).get("model", "gpt-4o-mini")
        api_key_env = config.get("openai", {}).get("api_key_env", "OPENAI_API_KEY")

        self.client = OpenAI(api_key=os.getenv(api_key_env))

        retry_config = config.get("openai", {}).get("retry", {})
        self.max_attempts = retry_config.get("max_attempts", 3)
        self.initial_delay = retry_config.get("initial_delay", 1)
        self.max_delay = retry_config.get("max_delay", 30)
        self.exponential_base = retry_config.get("exponential_base", 2)

        self.rate_limit_delay = config.get("openai", {}).get("rate_limit_delay", 0.5)

    def _apply_rate_limit(self):
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _get_retry_decorator(self):
        return retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.initial_delay,
                max=self.max_delay,
                exponential_base=self.exponential_base
            ),
            retry=retry_if_exception_type((RateLimitError, APIError, Timeout)),
            reraise=True
        )

    def _call_openai(self, system_prompt: str, user_prompt: str, response_format):
        self._apply_rate_limit()

        retry_decorator = self._get_retry_decorator()
        decorated_func = retry_decorator(self._make_api_call)
        return decorated_func(system_prompt, user_prompt, response_format)

    def _make_api_call(self, system_prompt: str, user_prompt: str, response_format):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format,
            temperature=0
        )
        return response

    def extract_event_list(self, markdown: str) -> dict:
        system_prompt = """You are an expert at extracting structured event data from markdown content.
Extract the events into the specified JSON schema format."""

        user_prompt = f"""Extract the list of events from the markdown content, as well as the link to the next page of events if one exists. Make sure to get every event. Do not skip events.

Markdown content:
{markdown}"""

        response = self._call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=EventListSchema
        )

        event_list = response.choices[0].message.parsed
        event_list.clean()

        return event_list.model_dump()

    def extract_event(self, markdown: str) -> dict:
        system_prompt = """You are an expert at extracting structured event data from markdown content.
Extract the event into the specified JSON schema format."""

        user_prompt = f"""Extract a single event from this markdown content.
Return the data in the Event schema format.

Markdown content:
{markdown}"""

        response = self._call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format=Event
        )

        event = response.choices[0].message.parsed
        event.clean()

        return event.model_dump()
