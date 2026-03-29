import argparse
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from lib.config.yaml_config_loader import YamlConfigLoader
from lib.scraper.factory import ScraperFactory
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.event_data_manager.event_data_manager import EventDataManager


def main():
    parser = argparse.ArgumentParser(description="Agro CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("scrape-event-list", help="Fetch event data from venue event list pages")
    get_parser.add_argument("--venue-id", type=str, help="Specific venue ID")

    update_parser = subparsers.add_parser("scrape-event-pages", help="Fetch event data from known event page urls")
    update_parser.add_argument("--venue-id", type=str, help="Specific venue ID")
    update_parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD) to fetch events for")

    args = parser.parse_args()

    mysql_interface = MySQLInterface()
    scraper = ScraperFactory.get_scraper()
    event_data_manager = EventDataManager(scraper, mysql_interface)

    if args.command == "scrape-event-list":
        event_data_manager.scrape_event_list_pages(args.venue_id)
    elif args.command == "scrape-event-pages":
        event_data_manager.scrape_event_pages(venue_id=args.venue_id, date=args.date)


if __name__ == "__main__":
    main()
