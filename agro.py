import argparse
import os
from dotenv import load_dotenv

load_dotenv()

from lib.fetcher.fetcher import Fetcher
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.llm_interface.ollama import OllamaLlm
from lib.llm_interface.gemini import GeminiLlm
from lib.event_data_manager.event_data_manager import EventDataManager


def main():
    parser = argparse.ArgumentParser(description="Agro CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    get_parser = subparsers.add_parser("scrape-event-list-pages", help="Fetch new event data")
    get_parser.add_argument("--venue-id", type=str, help="Specific venue ID")

    update_parser = subparsers.add_parser("update-event-data", help="Update existing event data")
    update_parser.add_argument("--venue-id", type=str, help="Specific venue ID")

    args = parser.parse_args()

    mysql_interface = MySQLInterface()

    llm_provider = os.getenv("AGRO_LLM_PROVIDER", "ollama").lower()
    if llm_provider == "gemini":
        llm_interface = GeminiLlm()
    else:
        llm_interface = OllamaLlm()

    fetcher = Fetcher(llm_interface)
    event_data_manager = EventDataManager(fetcher, mysql_interface, llm_interface)

    if args.command == "scrape-event-list-pages":
        event_data_manager.scrape_event_list_pages(args.venue_id)


if __name__ == "__main__":
    main()
