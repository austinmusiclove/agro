import json


def get_staged_transactions(conn, target_table):
    with conn.cursor() as cursor:
        sql = """
            SELECT
                st.*,
                e_current.title as current_event_title,
                e_current.venue_id as current_venue_id,
                e_current.start_date as current_start_date,
                e_staged.title as staged_event_title,
                e_staged.venue_id as staged_venue_id,
                e_staged.start_date as staged_start_date
            FROM staged_transactions st
            LEFT JOIN events e_current ON st.current_data_id = e_current.id
            LEFT JOIN events e_staged ON st.staged_data_id = e_staged.id
            WHERE st.target_table = %s
            AND st.status = 'pending-review';
        """
        cursor.execute(sql, (target_table,))
        records = cursor.fetchall()

        # Serialize to handle DateTime and Decimal objects safely for JSON consumption
        return json.loads(json.dumps(records, default=str))


def get_staged_transaction(conn, transaction_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM staged_transactions WHERE id = %s", (transaction_id,))
        transaction = cursor.fetchone()
        
        if not transaction:
            return None
            
        return json.loads(json.dumps(transaction, default=str))


def insert_staged_transaction(conn, transaction_data):
    with conn.cursor() as cursor:
        columns = [
            "target_table", "current_data_id", "staged_data_id",
            "transaction_type", "data_index", "screenshot", "schema_blob",
            "scrape_url"
        ]
        values = [
            transaction_data.get("target_table"),
            transaction_data.get("current_data_id"),
            transaction_data.get("staged_data_id"),
            transaction_data.get("transaction_type"),
            transaction_data.get("data_index"),
            transaction_data.get("screenshot"),
            json.dumps(transaction_data.get("schema_blob")) if transaction_data.get("schema_blob") else None,
            transaction_data.get("scrape_url"),
        ]

        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)

        query = f"INSERT INTO staged_transactions ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        return cursor.lastrowid
