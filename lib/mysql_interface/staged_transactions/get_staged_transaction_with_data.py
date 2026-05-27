from lib.mysql_interface.events import events
from lib.mysql_interface.venues import venues
from lib.mysql_interface.staged_transactions import get_next_staged_transaction


def get_staged_transaction_with_data(connector, transaction_id):
    sql = "SELECT * FROM staged_transactions WHERE id = ?"
    transaction = connector.execute_query(sql, [transaction_id])
    transaction = transaction[0] if transaction else None

    if not transaction:
        return None

    if transaction.get("transaction_type") == "multiple":
        return _get_transactions_by_screenshot(connector, transaction)

    return _enrich_transaction_with_data(connector, transaction)


def _get_transactions_by_screenshot(connector, transaction):
    screenshot = transaction.get("screenshot")
    if not screenshot:
        transaction["transactions"] = []
        return transaction

    sql = "SELECT * FROM staged_transactions WHERE screenshot = ? AND id != ?"
    results = connector.execute_query(sql, [screenshot, transaction.get("id")])

    enriched = [
        _enrich_transaction_with_data(connector, txn)
        for txn in results
    ]

    transaction["transactions"] = enriched
    return transaction


def _enrich_transaction_with_data(connector, transaction):
    if transaction.get('staged_data_id'):
        target_table = transaction.get('target_table')
        data_id = transaction.get('staged_data_id')
        record = None

        if target_table == 'events':
            record = events.get_event_by_id(connector, data_id)
        elif target_table == 'venues':
            record = venues.get_venue_by_id(connector, data_id)

        if record:
            transaction['staged_data'] = record

    if transaction.get('current_data_id'):
        target_table = transaction.get('target_table')
        data_id = transaction.get('current_data_id')
        record = None

        if target_table == 'events':
            record = events.get_event_by_id(connector, data_id)
        elif target_table == 'venues':
            record = venues.get_venue_by_id(connector, data_id)

        if record:
            transaction['current_data'] = record

    venue_id = None
    if transaction.get('staged_data') and transaction['staged_data'].get('venue_id'):
        venue_id = transaction['staged_data']['venue_id']
    elif transaction.get('current_data') and transaction['current_data'].get('venue_id'):
        venue_id = transaction['current_data']['venue_id']

    if venue_id:
        transaction['venue_future_events'] = events.get_future_events_by_venue(connector, venue_id)
    else:
        transaction['venue_future_events'] = []

    next_id = get_next_staged_transaction.get_next_staged_transaction(connector, transaction.get('id'), transaction.get('target_table'))
    if next_id:
        transaction['next_transaction_id'] = next_id

    return transaction
