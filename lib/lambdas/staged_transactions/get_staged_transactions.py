lib/lambdas/staged_transactions/get_staged_transactions.py
import json
import math

def get_staged_transactions(mysql_interface, logger, target_table, page=1, page_size=20):
    try:
        offset = (page - 1) * page_size
        records = mysql_interface.get_staged_transactions(target_table, limit=page_size, offset=offset)
        total = mysql_interface.get_staged_transactions_count(target_table)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(records),
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': math.ceil(total / page_size) if total else 0,
                'transactions': records
            })
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }

def get_staged_transaction_by_id(mysql_interface, logger, transaction_id):
    try:
        transaction = mysql_interface.get_staged_transaction_with_data(transaction_id)

        if not transaction:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Transaction {transaction_id} not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(transaction)
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }

