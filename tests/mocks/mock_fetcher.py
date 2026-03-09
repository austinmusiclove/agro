class MockFetcher:
    def __init__(self, llm_interface):
        self.llm_interface = llm_interface
        self.fetched_urls = []

    def fetch(self, url):
        self.fetched_urls.append(url)
        return ""

    def fetch_all_pages(self, url, max_pages=10):
        # PSEUDO CODE
        pass
