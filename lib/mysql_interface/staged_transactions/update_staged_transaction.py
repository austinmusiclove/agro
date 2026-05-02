def update_staged_transaction(connector, transaction_id: int, updates: dict) -> int:
    if not updates:
        return 0

    set_clause = ", ".join([f"{col} = ?" for col in updates.keys()])
    values = list(updates.values()) + [transaction_id]

    query = f"UPDATE staged_transactions SET {set_clause} WHERE id = ?"
    return connector.execute_update(query, values)
