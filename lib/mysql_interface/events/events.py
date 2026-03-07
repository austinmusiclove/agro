import pymysql


def get_events_by_venue(conn, venue_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM live_music_events WHERE venue_name = %s AND date > NOW()",
            (venue_id,)
        )
        return cursor.fetchall()
