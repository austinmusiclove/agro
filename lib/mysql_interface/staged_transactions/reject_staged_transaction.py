from .update_staged_transaction import update_staged_transaction
from lib.mysql_interface.events import events


def reject_staged_transaction(connector, staged_transaction):
    staged_data_id = staged_transaction.get("staged_data_id")
    update_staged_transaction(connector, staged_transaction["id"], {"status": "rejected"})
    if staged_data_id:
        events.update_event(connector, staged_data_id, {"status": "processed"})
