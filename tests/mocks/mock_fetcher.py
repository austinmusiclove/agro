class MockFetcher:
    def __init__(self):
        self.fetched_urls = []

    def fetch(self, url):
        self.fetched_urls.append(url)
        return ""
