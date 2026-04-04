from abc import ABC, abstractmethod
import html2text


class FetchError(Exception):
    def __init__(self, url: str, status_code: int = None, reason: str = None):
        self.url = url
        self.status_code = status_code
        self.reason = reason
        message = f"Failed to fetch {url}"
        if status_code:
            message += f": {status_code}"
        if reason:
            message += f" {reason}"
        super().__init__(message)


class FetcherInterface(ABC):
    @abstractmethod
    def fetch(self, url: str, return_markdown: bool = False, return_screenshot: bool = False):
        pass

    def _convert_html_to_markdown(self, html: str) -> str:
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        return converter.handle(html)
