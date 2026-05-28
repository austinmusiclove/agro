from .update_staged_transaction import update_staged_transaction
from .get_staged_transaction_by_id import get_staged_transaction_by_id
from lib.mysql_interface.events import events


def reject_staged_transaction(connector, staged_transaction_id):
    staged_transaction = get_staged_transaction_by_id(connector, staged_transaction_id)
    if not staged_transaction:
        return

    staged_data_id = staged_transaction.get("staged_data_id")
    update_staged_transaction(connector, staged_transaction_id, {"status": "rejected"})
    if staged_data_id:
        events.update_event(connector, staged_data_id, {"status": "processed"})
