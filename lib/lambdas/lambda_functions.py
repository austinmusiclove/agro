from lib.lambdas import get_staged_transactions_events

def router(event, context):
    return get_staged_transactions_events.get_staged_transactions_events(event, context)
