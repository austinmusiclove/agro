from .update_staged_transaction import update_staged_transaction
from .get_staged_transaction_with_data import get_staged_transaction_with_data
from lib.mysql_interface.events import events


def approve_staged_transaction(connector, staged_transaction_id, override_data=None):
    staged_transaction = get_staged_transaction_with_data(connector, staged_transaction_id)

    if not staged_transaction:
        return None

    transaction_type = staged_transaction.get('transaction_type')
    staged_data = staged_transaction.get('staged_data')
    current_data_id = staged_transaction.get('current_data_id')
    staged_data_id = staged_transaction.get('staged_data_id')

    if override_data is not None:
        staged_data = override_data

    if transaction_type == 'create':
        published_data = staged_data.copy()
        published_data['status'] = 'published'
        event_id = events.insert_event(connector, published_data)
        update_staged_transaction(connector, staged_transaction_id, {
            'status': 'approved',
            'current_data_id': event_id
        })
        if staged_data_id:
            events.update_event(connector, staged_data_id, {'status': 'processed'})
        return {'event_id': event_id, 'transaction_type': 'create'}

    elif transaction_type == 'update':
        update_data = staged_data.copy()
        update_data['status'] = 'published'
        events.update_event(connector, current_data_id, update_data)
        update_staged_transaction(connector, staged_transaction_id, {'status': 'approved'})
        if staged_data_id:
            events.update_event(connector, staged_data_id, {'status': 'processed'})
        return {'event_id': current_data_id, 'transaction_type': 'update'}

    elif transaction_type == 'delete':
        events.update_event(connector, current_data_id, {'status': 'disabled'})
        update_staged_transaction(connector, staged_transaction_id, {'status': 'approved'})
        return {'event_id': current_data_id, 'transaction_type': 'delete'}

    elif transaction_type == 'multiple':
        update_staged_transaction(connector, staged_transaction_id, {'status': 'approved'})
        return {'transaction_type': 'multiple'}
