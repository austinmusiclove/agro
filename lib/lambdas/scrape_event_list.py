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
from lib.sqs_interface import SQSInterface

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
sqs_interface              = SQSInterface(config_loader)
event_data_manager         = EventDataManager(scraper, mysql_interface, sqs_interface=sqs_interface if sqs_interface.is_configured() else None)

def scrape_event_list(event, context):
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            venue_id = body.get('venue_id')

            if venue_id is not None:
                venue_id = int(venue_id)
            else:
                raise Exception("No venue_id provided")

            paginate = body.get('paginate', False)
            if isinstance(paginate, str):
                paginate = paginate.lower() == 'true'

            event_data_manager.scrape_event_list_pages(venue_id, paginate=paginate)
            print(f"Successfully processed venue {venue_id}")

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            raise e

    return {
        'statusCode': 200,
        'body': 'Processed batch successfully'
    }
