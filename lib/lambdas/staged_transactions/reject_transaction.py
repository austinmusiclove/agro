import json


def reject_transaction(mysql_interface, logger, transaction_id):
    try:
        transaction = mysql_interface.get_staged_transaction_with_data(transaction_id)

        if not transaction:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Transaction {transaction_id} not found'})
            }

        if transaction.get('status') != 'pending-review':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Transaction {transaction_id} has already been processed (status: {transaction.get("status")})'})
            }

        mysql_interface.update_staged_transaction(transaction_id, {'status': 'rejected'})

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transaction rejected',
                'transaction_id': transaction_id
            })
        }

    except Exception as e:
        logger.error(f"Error rejecting transaction {transaction_id}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
