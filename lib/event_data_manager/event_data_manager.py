class EventDataManager:
    def __init__(self, fetcher, mysql_interface, llm_interface):
        self.fetcher = fetcher
        self.mysql_interface = mysql_interface
        self.llm_interface = llm_interface

    def get_new_event_data(self, venue_id=None):
        print(f"get_new_event_data called with venue_id={venue_id}")

    def update_event_data(self, venue_id=None):
        print(f"update_event_data called with venue_id={venue_id}")
