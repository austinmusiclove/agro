import json

from .reject_transaction import reject_transaction


def reject_transactions_bulk(mysql_interface, logger, transaction_ids):
    try:
        results = []
        for transaction_id in transaction_ids:
            try:
                response = reject_transaction(mysql_interface, logger, transaction_id)
                results.append({
                    'transaction_id': transaction_id,
                    'status': response['statusCode'],
                    'success': response['statusCode'] == 200,
                    'error': json.loads(response['body']).get('error') if response['statusCode'] != 200 else None
                })
            except Exception as e:
                logger.error(f"Error rejecting transaction {transaction_id}: {e}")
                results.append({
                    'transaction_id': transaction_id,
                    'status': 500,
                    'success': False,
                    'error': str(e)
                })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'total': len(transaction_ids),
                'rejected': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success']),
                'results': results
            })
        }

    except Exception as e:
        logger.error(f"Error bulk rejecting transactions: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
