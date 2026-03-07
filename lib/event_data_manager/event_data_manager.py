class EventDataManager:
    def __init__(self, fetcher, mysql_interface, llm_interface):
        self.fetcher = fetcher
        self.mysql_interface = mysql_interface
        self.llm_interface = llm_interface

    def get_new_event_data(self, venue_id=None):
        venues = self._get_venues(venue_id)
        # FOR each Venue:
        #     Pull events URL from venue DB
        #     Crawl all Event List Pages
        #     FOR each Event List Page:
        #         Convert HTML to Markdown
        #         Use LLM to find Event Page URLs in Markdown
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
        # FOR each Venue:
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
            return [self.mysql_interface.get_venue_by_id(venue_id)]
        else:
            return self.mysql_interface.get_all_venues()

