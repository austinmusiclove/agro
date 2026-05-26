def _scrape_event_page(self, event):
    event_id = event.get("id")
    event_page_url = event.get("event_page_url")
    if not event_page_url:
        print(f"Event {event_id} has no event_page_url.")
        return

    event_status = event.get("status")

    if event_status == "published":
        scrape_result = self.scraper.scrape_event_page(event)
        scraped_data = scrape_result.get("event")
        is_match = self._events_match(scraped_data, event)
        if scraped_data and not is_match:
            txn_data = {
                "status": "pending-review",
                "transaction_type": "update",
                "current_data_id": event_id,
                "screenshot": scraped_data.get("event_page_screenshot"),
                "scrape_url": scraped_data.get("event_page_url"),
                "scrape_html_hash": scraped_data.get("event_page_html_hash"),
                "scrape_markdown_hash": scraped_data.get("event_page_markdown_hash"),
            }
            self.mysql_interface.stage_transaction("events", scraped_data, txn_data)

    elif event_status == "staged":
        existing_txn = self.mysql_interface.get_staged_transaction_by_staged_data_id(event_id, "events")
        if existing_txn.get("status") == "pending-scrape" or existing_txn.get("status") == "pending-review":
            scrape_result = self.scraper.scrape_event_page(event)
            scraped_data = scrape_result.get('event')
            updated_event_data = event | scraped_data
            is_match = self._events_match(updated_event_data, event)
            if scraped_data and not is_match:
                self.mysql_interface.update_event(event_id, updated_event_data)
            # if there is schema, try to publish an event with the schema
            # update existing_txn to add new current data id as the id of the new published event
        if existing_txn.get("status") == "pending-scrape":
            self.mysql_interface.update_staged_transaction(existing_txn.get("id"), {'status': 'pending-review'})

    else:
        print(f"Event {event.get("id")} has status {event_status}. Only published and staged status are supported.")
        return


def _events_match(self, scraped_event, existing_event):
    fields_to_check = [
        "title", "start_date", "end_date", "start_time", "end_time",
        "ages", "price_range", "image_url", "ticket_url",
        "event_page_url", "page_schema"
    ]
    return all(scraped_event.get(f) == existing_event.get(f) for f in fields_to_check)
