class EventDataManager:
    def __init__(self, scraper, mysql_interface):
        self.scraper = scraper
        self.mysql_interface = mysql_interface

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
            scraped_events = self.scraper.scrape_event_list_page(event_list_url, paginate=True, max_pages=5)

            if scraped_events:
                print(f"Scraped {len(scraped_events)} events.")
                # TODO: Retrieve all events from db for this venue
                # current_events = self.mysql_interface.get_events_by_venue(venue.get("id"))

                # TODO: merge_events(scraped_events, current_events)
                # this function will delete events that are no longer appearing in scrape,
                # update events that are in scrape and db, and add events that are in scrape but not db
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
