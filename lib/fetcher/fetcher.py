import urllib.request
from urllib.error import URLError, HTTPError
import html2text


class Fetcher:
    def __init__(self, llm_interface):
        self.llm_interface = llm_interface

    def fetch(self, url, return_markdown=False, return_screenshot=False):
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    html = response.read().decode('utf-8')
                    if return_markdown:
                        return self._convert_html_to_markdown(html)
                    return html
                else:
                    raise HTTPError(url, response.status, "Non-200 response", {}, None)
        except HTTPError:
            raise
        except URLError as e:
            raise URLError(f"Failed to fetch {url}: {e.reason}") from e

    # Returns a list of pages as markdown. Returns the URL plus all pages if there is pagination up until the max_pages limit
    def fetch_all_pages(self, url, max_pages=10):
        pages = []
        current_url = url

        for _ in range(max_pages):
            markdown = self.fetch(current_url, return_markdown=True)
            pages.append(markdown)

            next_page_url = self.llm_interface.get_next_page_url(markdown, current_url)

            if not next_page_url:
                break

            current_url = next_page_url

        return pages

    def _convert_html_to_markdown(self, html):
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        return converter.handle(html)

