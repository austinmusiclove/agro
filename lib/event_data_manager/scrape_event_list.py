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

        existing_events = self.mysql_interface.get_future_events_by_venue(venue.get("id"))
        transactions = self._merge_events(existing_events, events)
        print(f"Processing {len(transactions)} transactions...")

        screenshots_with_creates = set()

        for txn in transactions:
            event_data = None
            txn_type = txn.get("transaction_type")
            txn_data = {
                "transaction_type": txn_type,
                "current_data_id": txn.get("existing_event_id"),
            }
            if txn_type == "create":
                event_data = txn.get("event_data").copy()
                txn_data["status"] = "pending-scrape" if event_data.get("event_page_url") else "pending-review"
                txn_data["screenshot"] = event_data.get("event_list_screenshot")
                screenshots_with_creates.add(event_data.get("event_list_screenshot"))
                txn_data["data_index"] = event_data.get("data_index")
                txn_data["scrape_url"] = event_data.get("scrape_url")
                txn_data["scrape_html_hash"] = event_data.get("event_list_html_hash")
                txn_data["scrape_markdown_hash"] = event_data.get("event_list_markdown_hash")
            elif txn_type == "delete":
                txn_data["status"] = "pending-review"

            result = self.mysql_interface.stage_transaction("events", event_data, txn_data)
            if self.sqs_interface and self.sqs_interface.is_configured() and result.get("staged_data_id"):
                self.sqs_interface.send_event_id(result["staged_data_id"])

        pages = scraped_result.get("pages", [])
        for page in pages:
            # skip if there were no transactions associated with this page
            screenshot = page.get("screenshot")
            if not screenshot:
                continue
            if screenshot not in screenshots_with_creates:
                continue
            self.mysql_interface.insert_staged_transaction({
                "status": "pending-review",
                "transaction_type": "multiple",
                "target_table": "events",
                "screenshot": screenshot,
                "scrape_url": page.get("scrape_url"),
                "scrape_html_hash": page.get("scrape_html_hash"),
                "scrape_markdown_hash": page.get("scrape_markdown_hash"),
            })

    else:
        print(f"No events scraped for {venue.get('name', venue.get('id'))}")


def _merge_events(self, existing_events, scraped_events):
    transactions = []
    matched_existing_ids = set()

    for event in scraped_events:
        match = self._find_event_match(event, existing_events)
        if match:
            matched_existing_ids.add(match["id"])
            # skip adding update to transactions so that updates only happen when updating an existing published event in the db not during an event list scrape
        else:
            transactions.append({
                "transaction_type": "create",
                "existing_event_id": None,
                "event_data": event
            })

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
