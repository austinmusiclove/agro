import logging

from lib.config.yaml_config_loader import YamlConfigLoader
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.lambdas import get_staged_transactions_events

config_loader = YamlConfigLoader(config_overrides=config_overrides)
mysql_interface = MySQLInterface(config_loader)
mysql_interface.connect()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def router(event, context):
    resource = event.get('resource')
    method = event.get('httpMethod')

    if resource == '/staged-transactions/events':
        return get_staged_transactions_events.get_staged_transactions_events(mysql_interface, logger)

    return {
        'statusCode': 404,
        'body': 'Not Found'
    }
