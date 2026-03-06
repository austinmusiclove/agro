class MockMySQLInterface:
    def __init__(self):
        self.venues = []
        self.events = []

    def get_venues(self):
        return self.venues

    def get_venue_by_id(self, venue_id):
        for venue in self.venues:
            if venue["id"] == venue_id:
                return venue
        return None
