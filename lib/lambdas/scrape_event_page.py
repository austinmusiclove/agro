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
    # 1. SQS sends a list of records
    for record in event['Records']:
        try:
            # 2. The message body is a string, you must parse it
            body = json.loads(record['body'])
            event_id = body.get('event_id')

            # 3. Your existing integer logic
            if event_id is not None:
                event_id = int(event_id)
            else:
                print("No event_id found in message body")
                continue # Skip this message

            # 4. Run your logic
            result = event_data_manager.scrape_event_page_by_event_id(event_id)
            print(f"Successfully processed {event_id}")

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            # In SQS triggers, if you want the message to stay in the queue to retry,
            # you must raise an exception here.
            raise e

    return {
        'statusCode': 200,
        'body': 'Processed batch successfully'
    }
