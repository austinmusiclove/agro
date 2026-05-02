import json
from lib.mysql_interface.events import events
from lib.mysql_interface.venues import venues


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


def get_staged_transaction_with_data(conn, transaction_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM staged_transactions WHERE id = %s", (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            return None

        if transaction and transaction.get('staged_data_id'):
            target_table = transaction.get('target_table')
            data_id = transaction.get('staged_data_id')
            record = None

            if target_table == 'events':
                record = events.get_event_by_id(conn, data_id)
            elif target_table == 'venues':
                record = venues.get_venue_by_id(conn, data_id)

            if record:
                transaction['staged_data'] = json.loads(json.dumps(record, default=str))

        return json.loads(json.dumps(transaction, default=str))


def insert_staged_transaction(conn, transaction_data):
    with conn.cursor() as cursor:
        columns = [
            "target_table", "current_data_id", "staged_data_id",
            "transaction_type", "data_index", "screenshot",
            "scrape_url", "scrape_html_hash", "scrape_markdown_hash"
        ]
        values = [
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

        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)

        query = f"INSERT INTO staged_transactions ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        return cursor.lastrowid


def update_staged_transaction(conn, transaction_id: int, updates: dict) -> int:
    if not updates:
        return 0

    with conn.cursor() as cursor:
        set_clause = ", ".join([f"{col} = %s" for col in updates.keys()])
        values = list(updates.values()) + [transaction_id]

        query = f"UPDATE staged_transactions SET {set_clause} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()

        return cursor.rowcount
