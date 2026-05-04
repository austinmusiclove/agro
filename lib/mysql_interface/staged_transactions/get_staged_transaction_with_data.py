from lib.mysql_interface.events import events
from lib.mysql_interface.venues import venues
from lib.mysql_interface.staged_transactions import get_next_staged_transaction


def get_staged_transaction_with_data(connector, transaction_id):
    sql = "SELECT * FROM staged_transactions WHERE id = ?"
    transaction = connector.execute_query(sql, [transaction_id])
    transaction = transaction[0] if transaction else None

    if not transaction:
        return None

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

    next_id = get_next_staged_transaction.get_next_staged_transaction(connector, transaction_id)
    if next_id:
        transaction['next_transaction_id'] = next_id

    return transaction
