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
        transaction["venue_future_events"] = {}
        return transaction

    sql = "SELECT * FROM staged_transactions WHERE screenshot = ? AND id != ?"
    results = connector.execute_query(sql, [screenshot, transaction.get("id")])

    enriched = [
        _enrich_transaction_with_data(connector, txn, venue_events=False)
        for txn in results
    ]

    venue_ids = set()
    for child in enriched:
        vid = _get_venue_id(child)
        if vid:
            venue_ids.add(vid)

    venue_future_events = {}
    for vid in venue_ids:
        venue_future_events[vid] = events.get_future_events_by_venue(connector, vid)

    transaction["transactions"] = enriched
    transaction["venue_future_events"] = venue_future_events

    next_id = get_next_staged_transaction(connector, transaction.get('id'), transaction.get('target_table'))
    if next_id:
        transaction['next_transaction_id'] = next_id

    return transaction


def _enrich_transaction_with_data(connector, transaction, venue_events=True):
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

    if venue_events:
        transaction['venue_future_events'] = _get_venue_future_events(connector, transaction)

    next_id = get_next_staged_transaction(connector, transaction.get('id'), transaction.get('target_table'))
    if next_id:
        transaction['next_transaction_id'] = next_id

    return transaction


def _get_venue_future_events(connector, transaction):
    venue_id = _get_venue_id(transaction)
    if venue_id:
        return {venue_id: events.get_future_events_by_venue(connector, venue_id)}
    return {}


def _get_venue_id(transaction):
    if transaction.get('staged_data') and transaction['staged_data'].get('venue_id'):
        return transaction['staged_data']['venue_id']
    if transaction.get('current_data') and transaction['current_data'].get('venue_id'):
        return transaction['current_data']['venue_id']
    return None
