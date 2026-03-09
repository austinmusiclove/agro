import urllib.request
from urllib.error import URLError, HTTPError
import html2text


class Fetcher:
    def __init__(self, llm_interface):
        self.llm_interface = llm_interface

    def fetch(self, url, return_markdown=False):
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
        # Fetch the initial page using fetch()
        markdown = self.fetch(url, True)

        # Use LLM to find next page button in Markdown
        next_page_url = self.llm_interface.get_next_page_url(markdown)
        # FOR each pagination link:
        #     Fetch the page using fetch()
        #     Stop if max_pages limit reached

        # RETURN list of pages
        pass

    def _convert_html_to_markdown(self, html):
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        return converter.handle(html)

