def get_staged_transaction_by_staged_data_id(connector, staged_data_id, target_table):
    sql = "SELECT * FROM staged_transactions WHERE staged_data_id = ? AND target_table = ?"
    result = connector.execute_query(sql, [staged_data_id, target_table])
    return result[0] if result else None
