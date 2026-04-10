from .interface import ScraperInterface
from lib.schemas.event import Event


class AgroScraper(ScraperInterface):
    def __init__(self, fetcher_factory, data_extractor_factory, config_loader):
        self._fetcher_factory        = fetcher_factory
        self._data_extractor_factory = data_extractor_factory
        self.fetcher                 = self._fetcher_factory.create()
        self.data_extractor          = self._data_extractor_factory.create()
        self._config_loader          = config_loader

    def scrape_event_list_page(self, url: str, paginate: bool = True, max_pages: int = 10) -> dict:
        all_events = []
        screenshots = []
        scraped_urls = set()
        current_url = url
        page_count = 0


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

                if screenshot:
                    screenshots.append(screenshot)

                if markdown:
                    extracted = self.data_extractor.extract_event_list(markdown)

                    events_on_page = extracted.get("events", [])
                    for index, event_dict in enumerate(events_on_page):
                        event_dict["screenshot_index"] = page_count
                        event_dict["data_source"] = "agro_scraper"
                        event_dict["scrape_url"] = current_url
                        event_dict["data_index"] = index
                        event_dict["html_hash"] = html_hash
                        event_dict["markdown_hash"] = markdown_hash
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
            "screenshots": screenshots
        }
