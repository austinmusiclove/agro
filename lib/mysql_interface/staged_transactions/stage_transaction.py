from lib.mysql_interface.events import events
from .insert_staged_transaction import insert_staged_transaction


def stage_transaction(connector, target_table: str, data: dict, txn_data: dict) -> dict:
    """
    Saves a staged record to the target table and creates a staged_transaction record for manual review.

    Args:
        connector: Database connector
        target_table: Name of the table to insert the staged record into
        data: Dict of column names and values to insert
        txn_data: Dict containing:
            - transaction_type: 'create', 'update', or 'delete'
            - current_data_id: ID of existing record (None for create)
            - data_index: Optional index that denotes the position of this data item in the screenshot
            - screenshot: Optional screenshot reference
            - scrape_url: URL that was scraped
            - scrape_html_hash: Optional SHA256 hash of the scraped HTML
            - scrape_markdown_hash: Optional SHA256 hash of the scraped markdown

    Returns:
        Dict with 'staged_data_id' and 'staged_transaction_id'
    """
    staged_data_id = None
    data_with_status = data.copy()
    data_with_status["status"] = "staged"
    txn_type = txn_data.get("transaction_type")

    if txn_type == "create" or txn_type == "update":
        if target_table == "events":
            staged_data_id = events.insert_event(connector, data_with_status)

    staged_txn_data = txn_data.copy()
    staged_txn_data["target_table"] = target_table
    staged_txn_data["staged_data_id"] = staged_data_id
    staged_transaction_id = insert_staged_transaction(connector, staged_txn_data)

    return {
        "staged_data_id": staged_data_id,
        "staged_transaction_id": staged_transaction_id
    }
