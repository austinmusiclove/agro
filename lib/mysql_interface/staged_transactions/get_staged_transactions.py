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
        ORDER BY COALESCE(e_staged.venue_id, e_current.venue_id), COALESCE(e_staged.start_date, e_current.start_date) ASC, st.id ASC
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
        WITH txn_info AS (
            SELECT
                COALESCE(e2.venue_id, e2c.venue_id) AS effective_venue_id,
                COALESCE(e2.start_date, e2c.start_date) AS effective_start_date
            FROM staged_transactions st2
            LEFT JOIN {target_table} e2 ON st2.staged_data_id = e2.id
            LEFT JOIN {target_table} e2c ON st2.current_data_id = e2c.id
            WHERE st2.id = ?
        )
        SELECT st.id FROM staged_transactions st
        LEFT JOIN {target_table} e_staged ON st.staged_data_id = e_staged.id
        LEFT JOIN {target_table} e_current ON st.current_data_id = e_current.id
        CROSS JOIN txn_info
        WHERE st.status = ?
          AND st.target_table = ?
          {type_clause}
          AND (
              COALESCE(e_staged.venue_id, e_current.venue_id) > txn_info.effective_venue_id
              OR (COALESCE(e_staged.venue_id, e_current.venue_id) = txn_info.effective_venue_id
                  AND COALESCE(e_staged.start_date, e_current.start_date) > txn_info.effective_start_date)
              OR (COALESCE(e_staged.venue_id, e_current.venue_id) = txn_info.effective_venue_id
                  AND COALESCE(e_staged.start_date, e_current.start_date) = txn_info.effective_start_date
                  AND st.id > ?)
          )
        ORDER BY COALESCE(e_staged.venue_id, e_current.venue_id), COALESCE(e_staged.start_date, e_current.start_date) ASC, st.id ASC
        LIMIT 1
    """
    result = connector.execute_query(sql, [transaction_id, status, target_table] + type_params + [transaction_id])
    return result[0].get('id') if result else None
