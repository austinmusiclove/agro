def insert_staged_transaction(connector, transaction_data):
    columns = [
        "status", "target_table", "current_data_id", "staged_data_id",
        "transaction_type", "data_index", "screenshot",
        "scrape_url", "scrape_html_hash", "scrape_markdown_hash"
    ]
    values = [
        transaction_data.get("status"),
        transaction_data.get("target_table"),
        transaction_data.get("current_data_id"),
        transaction_data.get("staged_data_id"),
        transaction_data.get("transaction_type"),
        transaction_data.get("data_index"),
        transaction_data.get("screenshot"),
        transaction_data.get("scrape_url"),
        transaction_data.get("scrape_html_hash"),
        transaction_data.get("scrape_markdown_hash"),
    ]

    placeholders = ", ".join(["?"] * len(columns))
    columns_str = ", ".join(columns)

    query = f"INSERT INTO staged_transactions ({columns_str}) VALUES ({placeholders})"
    return connector.execute_insert(query, values)
