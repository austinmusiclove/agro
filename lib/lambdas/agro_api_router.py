import logging
import re

from lib.config.yaml_config_loader import YamlConfigLoader
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.lambdas.staged_transactions import get_staged_transactions

config_loader = YamlConfigLoader(config_overrides={})
mysql_interface = MySQLInterface(config_loader)
mysql_interface.connect()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def router(event, context):
    resource = event.get('resource')
    method = event.get('httpMethod')

    if resource == '/staged-transactions/events':
        return get_staged_transactions.get_staged_transactions(mysql_interface, logger, 'events')

    if resource == '/staged-transactions/{id}':
        path_params = event.get('pathParameters')
        transaction_id = path_params.get('id')
        return get_staged_transactions.get_staged_transaction_by_id(mysql_interface, logger, transaction_id)

    return {
        'statusCode': 404,
        'body': 'Not Found'
    }
