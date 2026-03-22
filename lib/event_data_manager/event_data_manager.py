class EventDataManager:
    def __init__(self, scraper, mysql_interface):
        self.scraper = scraper
        self.mysql_interface = mysql_interface

    def scrape_event_list_pages(self, venue_id=None):
        venues = self._get_venues(venue_id)
        for venue in venues:
            events_url = venue.get("website_events_url")
            # get events from scraper(events_url, paginate=true)
            # if there are events get all events from db for this venue; else continue
            # events = merge_events(scraped_events, current_events); this function will delete events that are no longer appearing in scrape, update events that are in scrape and db, and add events that are in scrape but not db
        pass

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
