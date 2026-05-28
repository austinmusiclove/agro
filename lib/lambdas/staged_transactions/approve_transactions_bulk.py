import json


def approve_transactions_bulk(mysql_interface, logger, body):
    if not body or not isinstance(body, list):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Body must be a list of transactions'})
        }

    results = []
    for item in body:
        transaction_id = item.get('staged_transaction_id')
        override_data = item.get('override_data')

        if not transaction_id:
            results.append({
                'success': False,
                'error': 'Missing staged_transaction_id'
            })
            continue

        try:
            result = mysql_interface.approve_staged_transaction(transaction_id, override_data)
            results.append({
                'transaction_type': result.get('transaction_type'),
                'event_id': result.get('event_id'),
                'staged_transaction_id': transaction_id,
                'success': True
            })

        except Exception as e:
            logger.error(f"Error processing transaction {transaction_id}: {e}")
            results.append({
                'staged_transaction_id': transaction_id,
                'success': False,
                'error': str(e)
            })

    response = {'results': results}

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
