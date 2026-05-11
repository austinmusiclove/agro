import json
import boto3


class SQSInterface:
    def __init__(self, config_loader):
        config = config_loader.get_config("agro").get("sqs", {})
        self._queue_url = config.get("scrape_event_queue_url")
        self._client = boto3.client("sqs", region_name=config.get("region", "us-east-2")) if self._queue_url else None

    def is_configured(self) -> bool:
        return self._client is not None

    def send_event_id(self, event_id: int) -> dict | None:
        if not self._client:
            return None
        return self._client.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps({"event_id": event_id})
        )
