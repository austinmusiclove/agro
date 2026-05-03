import logging
import re

from lib.config.yaml_config_loader import YamlConfigLoader
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.lambdas.staged_transactions import get_staged_transactions
from lib.lambdas.staged_transactions import approve_transaction

config_loader           = YamlConfigLoader(config_overrides={})
mysql_connector_factory = MySQLConnectorFactory(config_loader)
mysql_connector         = mysql_connector_factory.create()
mysql_interface         = MySQLInterface(config_loader, mysql_connector)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def router(event, context):
    resource = event.get('resource')
    method = event.get('httpMethod')

    if resource == '/staged-transactions/events':
        if method == 'GET':
            return get_staged_transactions.get_staged_transactions(mysql_interface, logger, 'events')

    if resource == '/staged-transactions/{id}':
        if method == 'GET':
            path_params = event.get('pathParameters')
            transaction_id = path_params.get('id')
            return get_staged_transactions.get_staged_transaction_by_id(mysql_interface, logger, transaction_id)

    if resource == '/staged-transactions/{id}/approve':
        if method == 'POST':
            path_params = event.get('pathParameters')
            transaction_id = path_params.get('id')
            return approve_transaction.approve_transaction(mysql_interface, logger, transaction_id)

    return {
        'statusCode': 404,
        'body': 'Not Found'
    }
