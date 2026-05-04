import json


def get_next_staged_transaction(mysql_interface, logger, transaction_id):
    try:
        next_id = mysql_interface.get_next_staged_transaction(transaction_id)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'next_transaction_id': next_id
            })
        }

    except Exception as e:
        logger.error(f"Error getting next transaction after {transaction_id}: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
