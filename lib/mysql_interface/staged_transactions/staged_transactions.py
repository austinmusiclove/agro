import pymysql
import json


def insert_staged_transaction(conn, transaction_data):
    with conn.cursor() as cursor:
        columns = [
            "target_table", "current_data_row_id", "staged_data_id",
            "transaction_type", "data_index", "screenshot", "schema_blob",
            "scrape_url"
        ]
        values = [
            transaction_data.get("target_table"),
            transaction_data.get("current_data_row_id"),
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
