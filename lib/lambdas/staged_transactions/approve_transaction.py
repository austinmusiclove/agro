import json

from .approve_transactions_bulk import approve_transactions_bulk


def approve_transaction(mysql_interface, logger, transaction_id, override_data=None):
    try:
        transaction = mysql_interface.get_staged_transaction_by_id(transaction_id)
        transaction_type = transaction.get('transaction_type')

        if not transaction:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Transaction {transaction_id} not found'})
            }

        if transaction.get('status') == 'approved':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Transaction {transaction_id} has already been processed (status: {transaction.get("status")})'})
            }

        if transaction.get('target_table') != 'events':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Approval not supported for target_table: {transaction.get("target_table")}'})
            }

        if not transaction.get('staged_data_id') and transaction_type in ('create', 'update'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No staged data found for this transaction'})
            }

        if not transaction.get('current_data_id') and transaction_type in ('update', 'delete'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No current_data_id for this transaction'})
            }

        if transaction_type not in ('create', 'update', 'delete', 'multiple'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unsupported transaction type: {transaction_type}'})
            }

        result = mysql_interface.approve_staged_transaction(transaction_id, override_data)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transaction approved',
                'event_id': result['event_id'],
                'staged_transaction_id': transaction_id,
                'transaction_type': result['transaction_type']
            })
        }

    except Exception as e:
        logger.error(f"Error approving transaction {transaction_id}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
