from lib.lambdas import get_staged_transactions_events

def router(event, context):
    resource = event.get('resource')
    method = event.get('httpMethod')

    if resource == '/staged-transactions/events':
        return get_staged_transactions_events.get_staged_transactions_events(event, context)

    return {
        'statusCode': 404,
        'body': 'Not Found'
    }
