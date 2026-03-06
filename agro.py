import argparse

from lib.fetcher.fetcher import Fetcher
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.llm_interface.llm_interface import LlmInterface
from lib.event_data_manager.event_data_manager import EventDataManager


def main():
    parser = argparse.ArgumentParser(description="Agro CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("get-new-event-data", help="Fetch new event data")
    get_parser.add_argument("--venue-id", type=str, help="Specific venue ID")

    update_parser = subparsers.add_parser("update-event-data", help="Update existing event data")
    update_parser.add_argument("--venue-id", type=str, help="Specific venue ID")

    args = parser.parse_args()

    fetcher = Fetcher()
    mysql_interface = MySQLInterface()
    llm_interface = LlmInterface()
    event_data_manager = EventDataManager(fetcher, mysql_interface, llm_interface)

    if args.command == "get-new-event-data":
        event_data_manager.get_new_event_data(args.venue_id)
    elif args.command == "update-event-data":
        event_data_manager.update_event_data(args.venue_id)


if __name__ == "__main__":
    main()
