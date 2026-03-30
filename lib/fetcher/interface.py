from abc import ABC, abstractmethod
import html2text


class FetcherInterface(ABC):
    @abstractmethod
    def fetch(self, url: str, return_markdown: bool = False, return_screenshot: bool = False):
        pass

    def _convert_html_to_markdown(self, html: str) -> str:
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        return converter.handle(html)
