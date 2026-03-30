import urllib.request
from urllib.error import URLError, HTTPError
from .interface import FetcherInterface


class SimpleFetcher(FetcherInterface):
    def __init__(self):
        pass

    def fetch(self, url, return_markdown=False, return_screenshot=False):
        if return_screenshot:
            print("SimpleFetcher does not support screenshots. Returning HTML only.")
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
