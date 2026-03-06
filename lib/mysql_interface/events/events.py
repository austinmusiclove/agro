import pymysql


def get_events_by_venue(conn, venue_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM events WHERE venue_id = %s AND date > NOW()",
            (venue_id,)
        )
        return cursor.fetchall()
