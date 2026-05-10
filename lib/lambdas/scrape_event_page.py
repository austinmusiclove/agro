import json
from dotenv import load_dotenv
from lib.config.yaml_config_loader import YamlConfigLoader
from lib.scraper.factory import ScraperFactory
from lib.fetcher.factory import FetcherFactory
from lib.data_extractor.factory import DataExtractorFactory
from lib.image_saver.factory import ImageSaverFactory
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.event_data_manager.event_data_manager import EventDataManager

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

def scrape_event_page(event, context):
    # Safely get event_id from the top-level event dict
    event_id = event.get('event_id')

    # Explicitly cast to int if it's not None, otherwise keep it None
    if event_id is not None:
        try:
            event_id = int(event_id)
        except ValueError:
            event_id = None

    if event_id is None:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'event_id is required and must be a valid integer'
            })
        }

    return event_data_manager.scrape_event_page_by_event_id(event_id)
