def get_staged_transaction_by_id(connector, staged_transaction_id):
    sql = "SELECT * FROM staged_transactions WHERE id = ?"
    result = connector.execute_query(sql, [staged_transaction_id])
    return result[0] if result else None
