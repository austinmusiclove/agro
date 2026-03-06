class MockMySQLInterface:
    def __init__(self):
        self.venues = []
        self.events = []
        self._connection = None

    def close(self):
        pass

    def get_all_venues(self):
        return self.venues

    def get_venue_by_id(self, venue_id):
        for venue in self.venues:
            if venue["id"] == venue_id:
                return venue
        return None

    def get_events_by_venue(self, venue_id):
        return [e for e in self.events if e["venue_id"] == venue_id]
