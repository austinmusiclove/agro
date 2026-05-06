lib/mysql_interface/staged_transactions/get_next_staged_transaction.py
def get_next_staged_transaction(connector, transaction_id):
    sql = """
        SELECT st.id FROM staged_transactions st
        LEFT JOIN events e_staged ON st.staged_data_id = e_staged.id
        WHERE st.status = 'pending-review'
        AND (
            e_staged.start_date > (SELECT e2.start_date FROM staged_transactions st2 LEFT JOIN events e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?)
            OR (e_staged.start_date = (SELECT e2.start_date FROM staged_transactions st2 LEFT JOIN events e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?) AND st.id > ?)
        )
        ORDER BY e_staged.start_date ASC, st.id ASC
        LIMIT 1
    """
    result = connector.execute_query(sql, [transaction_id, transaction_id, transaction_id])
    return result[0].get('id') if result else None
