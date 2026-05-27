def _build_type_filter(transaction_type):
    if transaction_type is None:
        return "", []
    if isinstance(transaction_type, str):
        return "AND st.transaction_type = ?", [transaction_type]
    if isinstance(transaction_type, (list, tuple)):
        placeholders = ", ".join(["?"] * len(transaction_type))
        return f"AND st.transaction_type IN ({placeholders})", list(transaction_type)
    return "", []


def get_staged_transactions(connector, target_table, limit=None, offset=None, status='pending-review', transaction_type=None):
    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT ? OFFSET ?"

    type_clause, type_params = _build_type_filter(transaction_type)

    sql = f"""
        SELECT
            st.*,
            e_current.title as current_event_title,
            e_current.venue_id as current_venue_id,
            e_current.start_date as current_start_date,
            e_staged.title as staged_event_title,
            e_staged.venue_id as staged_venue_id,
            e_staged.start_date as staged_start_date,
            vs.name as staged_venue_name,
            vc.name as current_venue_name
        FROM staged_transactions st
        LEFT JOIN {target_table} e_current ON st.current_data_id = e_current.id
        LEFT JOIN {target_table} e_staged ON st.staged_data_id = e_staged.id
        LEFT JOIN venues vs ON e_staged.venue_id = vs.id
        LEFT JOIN venues vc ON e_current.venue_id = vc.id
        WHERE st.target_table = ?
        AND st.status = ?
        {type_clause}
        ORDER BY e_staged.venue_id, e_staged.start_date ASC, st.id ASC
        {limit_clause};
    """
    params = [target_table, status] + type_params
    if limit is not None:
        params.extend([limit, offset or 0])
    return connector.execute_query(sql, params)


def get_staged_transactions_count(connector, target_table, status='pending-review', transaction_type=None):
    type_clause, type_params = _build_type_filter(transaction_type)

    sql = f"""
        SELECT COUNT(*) as total
        FROM staged_transactions st
        WHERE st.target_table = ?
        AND st.status = ?
        {type_clause};
    """
    result = connector.execute_query(sql, [target_table, status] + type_params)
    return result[0]["total"] if result else 0


def get_next_staged_transaction(connector, transaction_id, target_table, status='pending-review', transaction_type=None):
    type_clause, type_params = _build_type_filter(transaction_type)

    sql = f"""
        SELECT st.id FROM staged_transactions st
        LEFT JOIN {target_table} e_staged ON st.staged_data_id = e_staged.id
        WHERE st.status = ?
        AND st.target_table = ?
        {type_clause}
        AND (
            e_staged.venue_id > (SELECT e2.venue_id FROM staged_transactions st2 LEFT JOIN {target_table} e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?)
            OR (e_staged.venue_id = (SELECT e2.venue_id FROM staged_transactions st2 LEFT JOIN {target_table} e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?)
                AND e_staged.start_date > (SELECT e2.start_date FROM staged_transactions st2 LEFT JOIN {target_table} e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?))
            OR (e_staged.venue_id = (SELECT e2.venue_id FROM staged_transactions st2 LEFT JOIN {target_table} e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?)
                AND e_staged.start_date = (SELECT e2.start_date FROM staged_transactions st2 LEFT JOIN {target_table} e2 ON st2.staged_data_id = e2.id WHERE st2.id = ?)
                AND st.id > ?)
        )
        ORDER BY e_staged.venue_id, e_staged.start_date ASC, st.id ASC
        LIMIT 1
    """
    result = connector.execute_query(sql, [status, target_table] + type_params + [transaction_id] * 6)
    return result[0].get('id') if result else None
