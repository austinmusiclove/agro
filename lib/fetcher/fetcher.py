import urllib.request
from urllib.error import URLError, HTTPError


class Fetcher:
    def __init__(self):
        pass

    def fetch(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return response.read().decode('utf-8')
                else:
                    raise HTTPError(url, response.status, "Non-200 response", {}, None)
        except HTTPError:
            raise
        except URLError as e:
            raise URLError(f"Failed to fetch {url}: {e.reason}") from e

    def fetch_with_pagination(self, url, max_pages=10):
        # Fetch the initial page using fetch()
        # Convert HTML to Markdown
        # Use LLM to find pagination links in Markdown
        # FOR each pagination link:
        #     Fetch the page using fetch()
        #     Stop if max_pages limit reached
        # RETURN list of HTML pages
        pass
