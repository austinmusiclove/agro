from .interface import ScraperInterface
from .json_ld_extractor import extract_event_schema
from lib.schemas.event import Event
from urllib.parse import urlparse


class AgroScraper(ScraperInterface):
    def __init__(self, fetcher_factory, data_extractor_factory, config_loader, image_saver):
        super().__init__(fetcher_factory, data_extractor_factory, config_loader, image_saver)

    def scrape_event_list_page(self, url: str, paginate: bool = True, max_pages: int = 10, venue: dict = None) -> dict:
        all_events = []
        scraped_urls = set()
        current_url = url
        page_count = 0

        parsed = urlparse(current_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        while current_url and page_count < max_pages:
            scraped_urls.add(current_url)

            try:
                print(f"Scraping event list page: {current_url}")

                result = self.fetcher.fetch(current_url, return_markdown=True, return_screenshot=True)

                html = result.get("html")
                markdown = result.get("markdown")
                screenshot = result.get("screenshot")
                html_hash = self._compute_hash(html)
                markdown_hash = self._compute_hash(markdown)

                screenshot_url = None
                if screenshot:
                    venue_name = venue.get("name")
                    name_hint = venue_name.replace(" ", "_").lower() if venue_name else "event_list"
                    screenshot_url = self.image_saver.save(screenshot, name_hint=f"{name_hint}_list_{page_count}")

                if markdown:
                    extracted = self.data_extractor.extract_event_list(markdown, base_url=base_url)

                    events_on_page = extracted.get("events", [])
                    for index, event_dict in enumerate(events_on_page):
                        if not event_dict.get("venue_id"): event_dict["venue_id"] = venue.get("id")
                        event_dict["event_list_screenshot"] = screenshot_url
                        event_dict["data_source"] = "agro_scraper"
                        event_dict["scrape_url"] = current_url
                        event_dict["data_index"] = index
                        event_dict["event_list_html_hash"] = html_hash
                        event_dict["event_list_markdown_hash"] = markdown_hash
                        all_events.append(event_dict)

                    if paginate:
                        next_url = extracted.get("next_page_url")
                        if next_url and next_url not in scraped_urls:
                            current_url = next_url
                            page_count += 1
                        else:
                            print(f"No new next page URL found or URL already scraped. Stopping pagination.")
                            break
                    else:
                        break
                else:
                    print(f"Failed to scrape {current_url}: No markdown returned from fetcher.")
                    break

            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
                break

        return {
            "events": all_events,
        }

    def scrape_event_page(self, event: dict) -> dict:
        event_data = {}
        event_page_url = event.get("event_page_url")
        if not event_page_url:
            print(f"Event {event.get("id")} has no event_page_url")
            return { "event": event_data, "schema_data": None }

        try:
            result = self.fetcher.fetch(event_page_url, return_markdown=True, return_screenshot=True)
        except Exception as e:
            print(f"Error scraping {event_page_url}: {e}")
            return { "event": event_data, "schema_data": None }

        html = result.get("html")
        markdown = result.get("markdown")
        screenshot = result.get("screenshot")
        html_hash = self._compute_hash(html)
        markdown_hash = self._compute_hash(markdown)

        schema_data = {}

        if html_hash != event.get("event_page_html_hash") and markdown_hash != event.get("event_page_markdown_hash"):

            schema_data = extract_event_schema(html)

            parsed = urlparse(event_page_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            event_data = self.data_extractor.extract_event(markdown, base_url=base_url, event_page_url=event_page_url)

            event_id = event.get("id")
            screenshot_ref = None
            if screenshot and self.image_saver:
                screenshot_ref = self.image_saver.save(screenshot, name_hint=f"event_{event_id}_page")

            event_data["id"] = event_id
            event_data["event_page_url"] = event_page_url
            event_data["event_page_screenshot"] = screenshot_ref
            event_data["event_page_html_hash"] = html_hash
            event_data["event_page_markdown_hash"] = markdown_hash
            event_data = event | event_data | schema_data

        return {
            "event": event_data,
            "schema_data": schema_data,
        }
