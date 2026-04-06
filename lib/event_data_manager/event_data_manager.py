class EventDataManager:
    def __init__(self, scraper, mysql_interface, image_saver=None):
        self.scraper = scraper
        self.mysql_interface = mysql_interface
        self.image_saver = image_saver

    def scrape_event_list_pages(self, venue_id=None):
        venues = self._get_venues(venue_id)
        if not venues:
            print("No venues found.")
            return

        for venue in venues:
            event_list_url = venue.get("website_events_url")
            if not event_list_url:
                print(f"Venue {venue.get('name', venue.get('id'))} has no website_events_url. Skipping.")
                continue

            print(f"Starting event list scrape for venue: {venue.get('name', venue.get('id'))}")
            scraped_result = self.scraper.scrape_event_list_page(event_list_url, paginate=True, max_pages=5)

            events = scraped_result.get("events", [])
            screenshots = scraped_result.get("screenshots", [])

            if events:
                print(f"Scraped {len(events)} events.")
                self._merge_events(venue_id, events)

                if screenshots and self.image_saver:
                    for idx, screenshot_bytes in enumerate(screenshots):
                        venue_name = venue.get("name", "unknown").replace(" ", "_").lower()
                        self.image_saver.save(screenshot_bytes, name_hint=f"{venue_name}_event_list_{idx}")
            else:
                print(f"No events scraped for {venue.get('name', venue.get('id'))}")
                continue

    def scrape_event_pages(self, venue_id=None, date=None):
        venues = self._get_venues(venue_id)
        for venue in venues:
            # Get all events from DB that have event page url and are not past
            # for each event
                # scrape to get structured data
                # merge scraped data with db record
            pass
        pass

    def scrape_event_page(self, event_page_url):
        pass

    def _get_venues(self, venue_id=None):
        if venue_id is not None:
            venue = self.mysql_interface.get_venue_by_id(venue_id)
            return [venue] if venue is not None else None
        else:
            return self.mysql_interface.get_all_venues()

    def _merge_events(self, venue_id, scraped_events):
        """ Updates events in database given a fresh set of scraped events for one venue """
        # current_events = self.mysql_interface.get_events_by_venue(venue.get("id"))
        # add any events that are not in current events
        # create proposed updates for any existing events in a separate table for review
        return scraped_events
