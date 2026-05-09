import argparse
import json
import os
from dotenv import load_dotenv
from lib.config.yaml_config_loader import YamlConfigLoader
from lib.scraper.factory import ScraperFactory
from lib.fetcher.factory import FetcherFactory
from lib.data_extractor.factory import DataExtractorFactory
from lib.image_saver.factory import ImageSaverFactory
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.event_data_manager.event_data_manager import EventDataManager
from lib.lambdas.staged_transactions import get_staged_transactions

from pathlib import Path
load_dotenv(override=True)

config_loader              = YamlConfigLoader()
fetcher_factory            = FetcherFactory(config_loader)
data_extractor_factory     = DataExtractorFactory(config_loader)
image_saver_factory        = ImageSaverFactory(config_loader)
image_saver                = image_saver_factory.create()
scraper_factory            = ScraperFactory(config_loader, fetcher_factory, data_extractor_factory, image_saver)
scraper                    = scraper_factory.create()
mysql_connector_factory    = MySQLConnectorFactory(config_loader)
mysql_connector            = mysql_connector_factory.create()
mysql_interface            = MySQLInterface(config_loader, mysql_connector)
event_data_manager         = EventDataManager(scraper, mysql_interface)

def scrape_event_list(event, context):
    # Safely get venue_id from the top-level event dict
    venue_id = event.get('venue_id')

    # Explicitly cast to int if it's not None, otherwise keep it None
    if venue_id is not None:
        try:
            venue_id = int(venue_id)
        except ValueError:
            venue_id = None # Fallback if someone passed a weird string

    # Get paginate parameter (default False)
    paginate = event.get('paginate', False)
    # Ensure it's a boolean
    if isinstance(paginate, str):
        paginate = paginate.lower() == 'true'

    return event_data_manager.scrape_event_list_pages(venue_id, paginate=paginate)
