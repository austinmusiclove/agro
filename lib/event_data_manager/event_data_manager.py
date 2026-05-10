class EventDataManager:
    def __init__(self, scraper, mysql_interface):
        self.scraper = scraper
        self.mysql_interface = mysql_interface

    def scrape_event_list_pages(self, venue_id=None, paginate=False):
        venues = self._get_venues(venue_id)
        if not venues:
            print("No venues found.")
            return
        for venue in venues:
            self._scrape_event_list(venue, paginate)

    def _scrape_event_list(self, venue, paginate):
        event_list_url = venue.get("website_events_url")
        if not event_list_url:
            print(f"Venue {venue.get('name', venue.get('id'))} has no website_events_url. Skipping.")
            return

        print(f"Starting event list scrape for venue: {venue.get('name', venue.get('id'))}")
        scraped_result = self.scraper.scrape_event_list_page(event_list_url, paginate=paginate, max_pages=4, venue=venue)
        events = scraped_result.get("events", [])

        if events:
            print(f"Scraped {len(events)} events.")

            # Merge newly scraped evetns with existing events to determine which ones should be created and deleted (updates are not done during event list scrape)
            existing_events = self.mysql_interface.get_future_events_by_venue(venue.get("id"))
            transactions = self._merge_events(existing_events, events)
            print(f"Processing {len(transactions)} transactions...")

            for txn in transactions:
                event_data = None
                txn_type = txn.get("transaction_type")
                txn_data = {
                    "transaction_type": txn_type,
                    "current_data_id": txn.get("existing_event_id"),
                }
                if txn_type == "create":
                    el_event_data = txn.get("event_data").copy()
                    ep_event_data = self.scraper.scrape_event_page(el_event_data)
                    event_data = el_event_data | ep_event_data
                    txn_data["screenshot"] = event_data.get("event_list_screenshot")
                    txn_data["data_index"] = event_data.get("data_index")
                    txn_data["scrape_url"] = event_data.get("scrape_url")
                    txn_data["scrape_html_hash"] = event_data.get("event_list_html_hash")
                    txn_data["scrape_markdown_hash"] = event_data.get("event_list_markdown_hash")

                self.mysql_interface.stage_transaction("events", event_data, txn_data)
        else:
            print(f"No events scraped for {venue.get('name', venue.get('id'))}")

    def scrape_event_pages(self, venue_id=None, date=None):
        venues = self._get_venues(venue_id)
        if not venues:
            print("No venues found.")
            return
        for venue in venues:
            existing_events = self.mysql_interface.get_future_events_by_venue(venue.get("id"))
            for event in existing_events:
                self._scrape_event_page(event)

    def _scrape_event_page(self, event):
        event_page_url = event.get("event_page_url")
        if not event_page_url:
            print(f"Event {event.get("id")} has no event_page_url.")
            return

        scraped_data = self.scraper.scrape_event_page(event)
        txn_data = {
            "transaction_type": 'update',
            "current_data_id": event.get("id"),
            "screenshot": scraped_data.get("event_page_screenshot"),
            "scrape_url": scraped_data.get("event_page_url"),
            "scrape_html_hash": scraped_data.get("event_page_html_hash"),
            "scrape_markdown_hash": scraped_data.get("event_page_markdown_hash"),
        }
        self.mysql_interface.stage_transaction("events", scraped_data, txn_data)

    def scrape_event_page_by_event_id(self, event_id):
        event = self.mysql_interface.get_event_by_id(event_id)
        if not event:
            print(f"Event {event_id} not found.")
            return
        if event.get("status") != "published":
            print(f"Event {event_id} is not published (status: {event.get('status')}). Skipping.")
            return
        self._scrape_event_page(event)

    def _get_venues(self, venue_id=None):
        if venue_id is not None:
            venue = self.mysql_interface.get_venue_by_id(venue_id)
            return [venue] if venue is not None else None
        else:
            return self.mysql_interface.get_all_venues()

    def _events_match(self, scraped_event, existing_event):
        """Check if all relevant fields match between a scraped event and an existing event."""
        fields_to_check = [
            "title", "start_date", "end_date", "start_time", "end_time",
            "ages", "price_range", "image_url", "ticket_url",
            "event_page_url"
        ]
        return all(scraped_event.get(f) == existing_event.get(f) for f in fields_to_check)

    def _merge_events(self, existing_events, scraped_events):
        """
        Compare scraped events against existing events in the database to determine what changes need to be made.

        Args:
            existing_events: List of existing event dicts
            scraped_events: List of event dicts from the scraper

        Returns:
            List of transaction dicts, each containing:
                - transaction_type: 'create' or 'delete'
                - existing_event_id: ID of matching existing event (None for create)
                - event_data: Event dict for create/update, None for delete
        """

        transactions = []
        matched_existing_ids = set()

        # Add create transactions
        for event in scraped_events:
            match = self._find_event_match(event, existing_events)
            if match:
                matched_existing_ids.add(match["id"])
            else:
                transactions.append({
                    "transaction_type": "create",
                    "existing_event_id": None,
                    "event_data": event
                })

        # Add delete transactions for existing events not in scraped
        for existing in existing_events:
            if existing["id"] not in matched_existing_ids:
                transactions.append({
                    "transaction_type": "delete",
                    "existing_event_id": existing["id"],
                    "event_data": None
                })

        return transactions

    def _find_event_match(self, event, existing_events):
            match = None
            event_page_url = event.get("event_page_url")
            existing_by_url = {e["event_page_url"]: e for e in existing_events if e.get("event_page_url")}

            if event_page_url and event_page_url in existing_by_url:
                match = existing_by_url.get(event_page_url)
            elif event_page_url:
                match = self.mysql_interface.get_event_by_event_page_url(event_page_url)
            return match
