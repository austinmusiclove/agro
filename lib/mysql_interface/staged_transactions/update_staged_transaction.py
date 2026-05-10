STAGED_TRANSACTION_COLUMNS = [
    "status", "target_table", "current_data_id", "staged_data_id",
    "transaction_type", "data_index", "screenshot",
    "scrape_url", "scrape_html_hash", "scrape_markdown_hash",
]


def update_staged_transaction(connector, transaction_id: int, updates: dict) -> int:
    updates = {k: v for k, v in updates.items() if k in STAGED_TRANSACTION_COLUMNS}

    if not updates:
        return 0

    set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
    values = list(updates.values()) + [transaction_id]

    query = f"UPDATE staged_transactions SET {set_clause} WHERE id = ?"
    return connector.execute_update(query, values)
