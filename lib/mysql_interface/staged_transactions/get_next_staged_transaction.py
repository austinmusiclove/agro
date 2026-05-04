def get_next_staged_transaction(connector, transaction_id):
    sql = """
        SELECT id FROM staged_transactions 
        WHERE id > ? AND status = 'pending-review'
        ORDER BY id ASC
        LIMIT 1
    """
    result = connector.execute_query(sql, [transaction_id])
    return result[0].get('id') if result else None
