class MockMySQLInterface:
    def __init__(self):
        self.venues = []
        self.events = []
        self._connection = None
        self.saved_transactions = []
        self.get_future_events_calls = []

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

    def get_future_events_by_venue(self, venue_id):
        self.get_future_events_calls.append(venue_id)
        return [e for e in self.events if e.get("venue_id") == venue_id]

    def stage_transaction(self, target_table, data, txn_data):
        self.saved_transactions.append({
            "target_table": target_table,
            "data": data,
            "txn_data": txn_data
        })
        return {
            "staged_data_id": 1,
            "staged_transaction_id": 1
        }

    def insert_staged_transaction(self, transaction_data):
        self.saved_transactions.append(transaction_data)
        return 1
