class MockFetcher:
    def __init__(self):
        self.fetched_urls = []

    def fetch(self, url):
        self.fetched_urls.append(url)
        return ""

    def fetch_with_pagination(self, url, max_pages=10):
        # PSEUDO CODE
        pass
