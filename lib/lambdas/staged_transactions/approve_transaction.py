import json


def approve_transaction(mysql_interface, logger, transaction_id, override_data=None):
    try:
        transaction = mysql_interface.get_staged_transaction_with_data(transaction_id)

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

        staged_data = transaction.get('staged_data')
        if not staged_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No staged data found for this transaction'})
            }

        published_data = staged_data.copy()
        published_data['status'] = 'published'

        # Apply any overrides passed in the request body
        if override_data:
            for key, value in override_data.items():
                published_data[key] = value

        published_event_id = mysql_interface.insert_event(published_data)

        mysql_interface.update_staged_transaction(transaction_id, {
            'status': 'approved',
            "current_data_id": published_event_id
        })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Transaction approved',
                'published_event_id': published_event_id,
                'transaction_id': transaction_id
            })
        }

    except Exception as e:
        logger.error(f"Error approving transaction {transaction_id}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
