class EventDataManager:
    def __init__(self, fetcher, mysql_interface, llm_interface):
        self.fetcher = fetcher
        self.mysql_interface = mysql_interface
        self.llm_interface = llm_interface

    def scrape_event_list_pages(self, venue_id=None):
        venues = self._get_venues(venue_id)
        for venue in venues:
            events_url = venue.get("website_events_url")
            event_list_pages = self.fetcher.fetch_all_pages(events_url, 10)
            for event_list_page in event_list_pages:
                event_urls = self.llm_interface.get_event_page_urls(event_list_page, current_url=events_url)
                for event_url in event_urls:
                    pass
            #     FOR each Event Page URL:
            #         Is URL in DB?
        #             Yes:
        #                 Was it updated since last crawled?
        #                     Yes:
        #                         Is there sitemap entry?
        #                             Yes: Extract or LLM → Save
        #                             No: Do Nothing
        #                     No: Do Nothing
        #             No (new):
        #                 Is there Event Schema?
        #                     Yes: Parse Schema → Save
        #                     No: Convert to Markdown → LLM → Save
        pass

    def update_event_data(self, venue_id=None):
        venues = self._get_venues(venue_id)
        for venue in venues:
            pass
        #     Get all events from DB that are not past
        #     FOR each Event:
        #         Get the Event Page URL
        #         Was it updated since last crawled?
        #             Yes:
        #                 Is there Event Schema?
        #                     Yes: Parse Schema → Update DB
        #                     No: Convert to Markdown → LLM → Update DB
        #             No: Do Nothing
        pass

    def _get_venues(self, venue_id=None):
        if venue_id is not None:
            venue = self.mysql_interface.get_venue_by_id(venue_id)
            return [venue] if venue is not None else None
        else:
            return self.mysql_interface.get_all_venues()
