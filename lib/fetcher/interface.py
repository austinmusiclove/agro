from abc import ABC, abstractmethod


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
    def __init__(self, config_loader=None):
        self._config_loader = config_loader
        self._config = self._load_config()

    def _load_config(self) -> dict:
        if self._config_loader:
            return self._config_loader.get_config("agro").get("fetcher", {})
        return {}

    @abstractmethod
    def fetch(self, url: str, return_markdown: bool = False, return_screenshot: bool = False):
        pass

    def _convert_html_to_markdown(self, html: str) -> str:
        import html2text
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        return converter.handle(html)
