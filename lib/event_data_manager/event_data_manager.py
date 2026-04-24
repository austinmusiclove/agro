class EventDataManager:
    def __init__(self, scraper, mysql_interface, image_saver=None):
        self.scraper = scraper
        self.mysql_interface = mysql_interface
        self.image_saver = image_saver

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
            scraped_result = self.scraper.scrape_event_list_page(event_list_url, paginate=True, max_pages=2)

            events = scraped_result.get("events", [])
            screenshots = scraped_result.get("screenshots", [])

            if events:
                print(f"Scraped {len(events)} events.")

                # Save screenshots first and get refs
                screenshot_refs = {}
                venue_name = venue.get("name", "unknown").replace(" ", "_").lower()
                if screenshots and self.image_saver:
                    for idx, screenshot_bytes in enumerate(screenshots):
                        img_ref = self.image_saver.save(screenshot_bytes, name_hint=f"{venue_name}_event_list_{idx}")
                        screenshot_refs[idx] = img_ref

                # Get transactions and process
                existing_events = self.mysql_interface.get_future_events_by_venue(venue.get("id"))
                transactions = self._merge_events(existing_events, events)
                print(f"Processing {len(transactions)} transactions...")
                for txn in transactions:

                    db_event = None
                    txn_type = txn.get("transaction_type")
                    txn_data = {
                        "transaction_type": txn_type,
                        "current_data_id": txn.get("existing_event_id"),
                        "schema_blob": txn["event_data"],
                    }
                    if txn_type == "create" or txn_type == "update":
                        db_event = txn.get("event_data").copy()
                        screenshot_idx = db_event.get("screenshot_index")
                        screenshot_ref = screenshot_refs.get(screenshot_idx) if screenshot_idx is not None else None
                        db_event["image_ref"] = screenshot_ref
                        db_event["venue_id"] = venue.get("id")
                        txn_data["screenshot"] = screenshot_ref
                        txn_data["data_index"] = db_event.get("data_index")
                        txn_data["scrape_url"] = db_event.get("scrape_url")
                        txn_data["scrape_html_hash"] = db_event.get("scrape_html_hash")
                        txn_data["scrape_markdown_hash"] = db_event.get("scrape_markdown_hash")

                    self.mysql_interface.stage_transaction("events", db_event, txn_data)
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

    def _merge_events(self, existing_events, scraped_events):
        """
        Compare scraped events against existing events in the database to determine what changes need to be made.

        Matching logic:
        - First tries to match by event_page_url
        - If no event_page_url, matches by start_date
        - If a scraped event matches an existing event: transaction_type = 'update'
        - If a scraped event has no match: transaction_type = 'create'
        - If an existing event has no match in scraped events: transaction_type = 'delete'

        Args:
            existing_events: List of existing event dicts
            scraped_events: List of event dicts from the scraper

        Returns:
            List of transaction dicts, each containing:
                - transaction_type: 'create', 'update', or 'delete'
                - existing_event_id: ID of matching existing event (None for create)
                - event_data: Event dict for create/update, None for delete
        """

        # Build lookup maps
        existing_by_url = {e["event_page_url"]: e for e in existing_events if e.get("event_page_url")}
        existing_by_date = {str(e["start_date"]): e for e in existing_events if e.get("start_date")}

        transactions = []
        scraped_urls = set()
        matched_existing_ids = set()

        # Classify scraped events
        for event in scraped_events:
            event_page_url = event.get("event_page_url")

            match = None
            if event_page_url:
                match = existing_by_url.get(event_page_url)
                scraped_urls.add(event_page_url)
            else:
                start_date = event.get("start_date")
                match = existing_by_date.get(str(start_date)) if start_date else None

            if match:
                matched_existing_ids.add(match["id"])
                txn_type = "update"
                existing_id = match["id"]
            else:
                txn_type = "create"
                existing_id = None

            transactions.append({
                "transaction_type": txn_type,
                "existing_event_id": existing_id,
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
