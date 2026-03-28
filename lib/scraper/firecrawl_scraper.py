import os
from firecrawl import FirecrawlApp
from firecrawl.v2.types import ScrapeOptions
from .interface import ScraperInterface
from lib.schemas.event_list import EventListSchema
from lib.schemas.event import Event

class FirecrawlScraper(ScraperInterface):
    def __init__(self):
        # We allow connecting to a local instance by grabbing the API URL from the environment
        # as well as the API key, providing defaults if they are missing.
        api_key = os.getenv("FIRECRAWL_API_KEY", "local-dev-key")
        api_url = os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
        self.firecrawl = FirecrawlApp(api_key=api_key, api_url=api_url)

    def scrape_event_list_page(self, url: str, paginate: bool = True, max_pages = 10) -> list[dict]:
        all_events = []
        scraped_urls = set()
        current_url = url
        page_count = 0

        while current_url and page_count < max_pages:
            scraped_urls.add(current_url)

            try:
                print(f"Scraping event list page: {current_url}")
                # We use the Firecrawl scrape endpoint with JSON formatting to structure the data using our schema
                res = self.firecrawl.scrape(
                    current_url,
                    formats=[
                        {
                        "type": "json",
                        "prompt": "Extract the list of events from this page, as well as the link to the next page of events if one exists. Make sure to get every event. Do not skip events.",
                        "schema": EventListSchema.model_json_schema()
                        },
                        #{ "type": "screenshot", "fullPage": True, "quality": 80 },
                    ],
                )

                if res:
                    # In python SDK v2, scrape() returns a Document Pydantic model
                    json_data = res.json if hasattr(res, 'json') else {}
                    if not json_data and hasattr(res, 'model_dump'):
                        # Maybe it is nested inside the dict dump
                        dumped = res.model_dump()
                        json_data = dumped.get("json", {})

                    if not json_data:
                        # Fallback if it acts like a dict in some versions
                        json_data = res.get("json", {}) if isinstance(res, dict) else {}

                    events_on_page = json_data.get("events", [])
                    for event_dict in events_on_page:
                        event = Event(**event_dict)
                        event.clean()
                        all_events.append(event)

                    if paginate:
                        next_url = json_data.get("next_page_url")
                        if next_url and next_url not in scraped_urls:
                            current_url = next_url
                            page_count += 1
                        else:
                            print(f"No new next page URL found or URL already scraped. Stopping pagination.")
                            break
                    else:
                        break
                else:
                    print(f"Failed to scrape {current_url}: No JSON data returned from Firecrawl.")
                    break

            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
                break

        return all_events
