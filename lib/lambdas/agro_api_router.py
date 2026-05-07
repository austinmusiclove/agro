import logging
import re
import json

from lib.config.yaml_config_loader import YamlConfigLoader
from lib.mysql_interface.mysql_interface import MySQLInterface
from lib.mysql_interface.mysql_connector.factory import MySQLConnectorFactory
from lib.lambdas.staged_transactions import get_staged_transactions
from lib.lambdas.staged_transactions import get_next_staged_transaction
from lib.lambdas.staged_transactions import approve_transaction
from lib.lambdas.staged_transactions import reject_transaction
from lib.lambdas.staged_transactions import reject_transactions_bulk
from lib.lambdas.events import get_future_events

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
            query_params = event.get('queryStringParameters') or {}
            page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', 20))
            return get_staged_transactions.get_staged_transactions(mysql_interface, logger, 'events', page, page_size)

    if resource == '/events/future':
        if method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            venue_id = int(query_params['venue_id']) if query_params.get('venue_id') else None
            page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', 20))
            return get_future_events.get_future_events(mysql_interface, logger, venue_id, page, page_size)

    if resource == '/staged-transactions/{id}':
        if method == 'GET':
            path_params = event.get('pathParameters')
            transaction_id = path_params.get('id')
            return get_staged_transactions.get_staged_transaction_by_id(mysql_interface, logger, transaction_id)

    if resource == '/staged-transactions/{id}/next':
        if method == 'GET':
            path_params = event.get('pathParameters')
            transaction_id = path_params.get('id')
            return get_next_staged_transaction.get_next_staged_transaction(mysql_interface, logger, transaction_id)

    if resource == '/staged-transactions/{id}/approve':
        if method == 'POST':
            path_params = event.get('pathParameters')
            transaction_id = path_params.get('id')
            body = event.get('body')
            override_data = json.loads(body) if body else {}
            return approve_transaction.approve_transaction(mysql_interface, logger, transaction_id, override_data)

    if resource == '/staged-transactions/{id}/reject':
        if method == 'POST':
            path_params = event.get('pathParameters')
            transaction_id = path_params.get('id')
            return reject_transaction.reject_transaction(mysql_interface, logger, transaction_id)

    if resource == '/staged-transactions/reject':
        if method == 'POST':
            body = event.get('body')
            if not body:
                return {'statusCode': 400, 'body': json.dumps({'error': 'Request body required'})}
            data = json.loads(body)
            transaction_ids = data.get('ids', [])
            return reject_transactions_bulk.reject_transactions_bulk(mysql_interface, logger, transaction_ids)

    return {
        'statusCode': 404,
        'body': 'Not Found'
    }
