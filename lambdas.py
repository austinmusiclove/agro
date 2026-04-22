from lib.lambdas import get_staged_transactions_events

def get_staged_transactions_events_handler(event, context):
    return get_staged_transactions_events.get_staged_transactions_events(event, context)
