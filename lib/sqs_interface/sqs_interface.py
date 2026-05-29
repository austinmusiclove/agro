import json
import boto3


class SQSInterface:
    def __init__(self, config_loader):
        config = config_loader.get_config("agro").get("sqs", {})
        self._event_page_queue_url = config.get("scrape_event_queue_url")
        self._event_list_queue_url = config.get("scrape_event_list_queue_url")
        region = config.get("region", "us-east-2")
        if self._event_page_queue_url or self._event_list_queue_url:
            self._client = boto3.client("sqs", region_name=region)
        else:
            self._client = None

    def is_configured(self) -> bool:
        return self._client is not None

    def send_event_id(self, event_id: int) -> dict | None:
        if not self._client or not self._event_page_queue_url:
            return None
        return self._client.send_message(
            QueueUrl=self._event_page_queue_url,
            MessageBody=json.dumps({"event_id": event_id})
        )

    def send_event_list_scrape(self, venue_id: int, paginate: bool = False) -> dict | None:
        if not self._client or not self._event_list_queue_url:
            return None
        return self._client.send_message(
            QueueUrl=self._event_list_queue_url,
            MessageBody=json.dumps({"venue_id": venue_id, "paginate": paginate})
        )

    def send_all_event_list_scrapes(self, mysql_interface, paginate=False) -> dict:
        if not self._client or not self._event_list_queue_url:
            return {'sent': 0, 'total': 0, 'errors': []}

        venues = mysql_interface.get_all_venues()
        sent = 0
        errors = []
        for venue in venues:
            if venue.get('website_events_url'):
                try:
                    self.send_event_list_scrape(venue['id'], paginate=paginate)
                    sent += 1
                except Exception as e:
                    errors.append({'venue_id': venue['id'], 'error': str(e)})

        return {'sent': sent, 'total': len(venues), 'errors': errors}
