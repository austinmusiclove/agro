import os
from firecrawl import FirecrawlApp
from .interface import ScraperInterface
from lib.schemas.event_list import EventListSchema

class FirecrawlScraper(ScraperInterface):
    def __init__(self):
        # We allow connecting to a local instance by grabbing the API URL from the environment
        # as well as the API key, providing defaults if they are missing.
        api_key = os.getenv("FIRECRAWL_API_KEY", "local-dev-key")
        api_url = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
        self.firecrawl = FirecrawlApp(api_key=api_key, api_url=api_url)

    def scrape_event_list_page(self, url: str, paginate: bool = True, max_pages = 10) -> list[dict]:
        all_events = []
        current_url = url
        page_count = 0

        while current_url and page_count < max_pages:
            try:
                print(f"Scraping event list page: {current_url}")
                # We use the Firecrawl scrape endpoint with JSON formatting to structure the data using our schema
                res = self.firecrawl.scrape(
                    current_url,
                    params={
                        "formats": ["json"],
                        "jsonOptions": {
                            "prompt": "Extract the list of upcoming events from this page, as well as the link to the next page of events if one exists.",
                            "schema": EventListSchema.model_json_schema()
                        }
                    }
                )

                if res and res.get("success"):
                    data = res.get("data", {})
                    # The json output is inside the json key of the data dict
                    json_data = data.get("json", {})

                    events_on_page = json_data.get("events", [])
                    all_events.extend(events_on_page)

                    if paginate:
                        current_url = json_data.get("next_page_url")
                        page_count += 1
                    else:
                        break
                else:
                    print(f"Failed to scrape {current_url}: {res.get('error')}")
                    break

            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
                break

        return all_events
