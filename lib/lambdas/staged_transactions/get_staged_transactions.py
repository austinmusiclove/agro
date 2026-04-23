import json

def get_staged_transactions(mysql_interface, logger, target_table):
    try:
        records = mysql_interface.get_staged_transactions(target_table)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(records),
                'transactions': records
            })
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
