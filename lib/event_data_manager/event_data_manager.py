from .scrape_event_list import _scrape_event_list, _merge_events, _find_event_match
from .scrape_event_page import _scrape_event_page, _events_match


class EventDataManager:
    _scrape_event_list = _scrape_event_list
    _scrape_event_page = _scrape_event_page
    _events_match = _events_match
    _merge_events = _merge_events
    _find_event_match = _find_event_match

    def __init__(self, scraper, mysql_interface, *, sqs_interface=None):
        self.scraper = scraper
        self.mysql_interface = mysql_interface
        self.sqs_interface = sqs_interface

    def scrape_event_list_pages(self, venue_id=None, paginate=False):
        venues = self._get_venues(venue_id)
        if not venues:
            print("No venues found.")
            return
        for venue in venues:
            self._scrape_event_list(venue, paginate)

    def scrape_event_pages(self, venue_id=None, date=None):
        venues = self._get_venues(venue_id)
        if not venues:
            print("No venues found.")
            return
        for venue in venues:
            existing_events = self.mysql_interface.get_future_events_by_venue(venue.get("id"))
            for event in existing_events:
                self._scrape_event_page(event)

    def scrape_event_page_by_event_id(self, event_id):
        event = self.mysql_interface.get_event_by_id(event_id)
        if not event:
            print(f"Event {event_id} not found.")
            return
        self._scrape_event_page(event)

    def _get_venues(self, venue_id=None):
        if venue_id is not None:
            venue = self.mysql_interface.get_venue_by_id(venue_id)
            return [venue] if venue is not None else None
        else:
            return self.mysql_interface.get_all_venues()