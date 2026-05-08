import time
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class DataExtractorInterface(ABC):
    @abstractmethod
    def extract_event_list(self, markdown: str, base_url: str = None) -> dict:
        """
        Extracts a list of events from markdown content.
        Returns a dictionary containing the list of events and optional next page URL.
        """
        pass

    @abstractmethod
    def extract_event(self, markdown: str, base_url: str = None) -> dict:
        """
        Extracts a single event from markdown content.
        Returns a dictionary representing the extracted event.
        """
        pass

    def _apply_rate_limit(self):
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def _get_retry_decorator(self, exception_types):
        return retry(
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=self.initial_delay,
                max=self.max_delay,
                exp_base=self.exponential_base
            ),
            retry=retry_if_exception_type(exception_types),
            reraise=True
        )
