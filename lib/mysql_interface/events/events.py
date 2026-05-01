import pymysql
from lib.helpers.helper import format_time


def get_event_by_id(conn, event_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM events WHERE id = %s",
            (event_id,)
        )
        return cursor.fetchone()

def get_future_events_by_venue(conn, venue_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, title, venue_id, start_date, event_page_url FROM events WHERE venue_id = %s AND start_date > NOW() AND status = 'published'",
            (venue_id,)
        )
        return cursor.fetchall()


def insert_event(conn, event_data):
    with conn.cursor() as cursor:
        columns = [
            "title", "venue_id", "start_date", "end_date", "start_time", "end_time",
            "ages", "price_range", "status", "data_source", "event_page_url", "ticket_url",
            "image_ref", "image_url"
        ]
        values = [
            event_data.get("title"),
            event_data.get("venue_id"),
            event_data.get("start_date"),
            event_data.get("end_date"),
            format_time(event_data.get("start_time")),
            format_time(event_data.get("end_time")),
            event_data.get("ages"),
            event_data.get("price"),
            event_data.get("status", "staged"),
            event_data.get("data_source"),
            event_data.get("event_page_url"),
            event_data.get("ticket_url"),
            event_data.get("image_ref"),
            event_data.get("image_url"),
        ]

        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)

        query = f"INSERT INTO events ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()

        return cursor.lastrowid
