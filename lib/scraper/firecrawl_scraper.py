import os
from firecrawl import FirecrawlApp
from .interface import ScraperInterface

class FirecrawlScraper(ScraperInterface):
    def __init__(self):
        # We allow connecting to a local instance by grabbing the API URL from the environment
        # as well as the API key, providing defaults if they are missing.
        api_key = os.getenv("FIRECRAWL_API_KEY", "local-dev-key")
        api_url = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
        self.app = FirecrawlApp(api_key=api_key, api_url=api_url)
