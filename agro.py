import argparse
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from lib.config.yaml_config_loader import YamlConfigLoader
from lib.scraper.factory import ScraperFactory
from lib.fetcher.factory import FetcherFactory
from lib.data_extractor.factory import DataExtractorFactory
from lib.image_saver.factory import ImageSaverFactory
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.event_data_manager.event_data_manager import EventDataManager
from lib.sqs_interface import SQSInterface


def main():
    parser = argparse.ArgumentParser(description="Agro CLI")
    parser.add_argument("--config-override", type=str, help="JSON string of config overrides")

    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("scrape-event-list", help="Fetch event data from venue event list pages")
    get_parser.add_argument("--venue-id", type=int, help="Specific venue ID")
    get_parser.add_argument("-p", "--paginate", action="store_true", help="Enable pagination for event list scraping")

    update_parser = subparsers.add_parser("scrape-event-pages", help="Fetch event data from known event page urls")
    update_parser.add_argument("--venue-id", type=int, help="Specific venue ID")
    update_parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD) to fetch events for")

    scrape_parser = subparsers.add_parser("scrape-event-page", help="Scrape a single event page by event ID")
    scrape_parser.add_argument("--event-id", type=int, required=True, help="Event ID of the event to scrape")

    queue_parser = subparsers.add_parser("queue-event-list-scrape", help="Queue a venue event list scrape via SQS")
    queue_parser.add_argument("--venue-id", type=int, required=True, help="Venue ID to scrape")

    args = parser.parse_args()

    config_overrides = {}
    if args.config_override:
        try:
            config_overrides = json.loads(args.config_override)
        except json.JSONDecodeError as e:
            print(f"Error parsing --config-override: {e}")
            return

    config_loader              = YamlConfigLoader(config_overrides=config_overrides)
    fetcher_factory            = FetcherFactory(config_loader)
    data_extractor_factory     = DataExtractorFactory(config_loader)
    image_saver_factory        = ImageSaverFactory(config_loader)
    image_saver                = image_saver_factory.create()
    scraper_factory            = ScraperFactory(config_loader, fetcher_factory, data_extractor_factory, image_saver)
    scraper                    = scraper_factory.create()
    mysql_connector_factory    = MySQLConnectorFactory(config_loader)
    mysql_connector            = mysql_connector_factory.create()
    mysql_interface            = MySQLInterface(config_loader, mysql_connector)
    sqs_interface              = SQSInterface(config_loader)
    event_data_manager         = EventDataManager(scraper, mysql_interface, sqs_interface=sqs_interface if sqs_interface.is_configured() else None)

    if args.command == "scrape-event-list":
        event_data_manager.scrape_event_list_pages(args.venue_id, paginate=args.paginate)
    elif args.command == "scrape-event-pages":
        event_data_manager.scrape_event_pages(venue_id=args.venue_id, date=args.date)
    elif args.command == "scrape-event-page":
        event_data_manager.scrape_event_page_by_event_id(args.event_id)
    elif args.command == "queue-event-list-scrape":
        sqs_interface.send_event_list_scrape(args.venue_id)


if __name__ == "__main__":
    main()
