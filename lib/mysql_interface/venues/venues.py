import pymysql


def get_venue_by_id(conn, venue_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM venues WHERE id = %s", (venue_id,))
        return cursor.fetchone()


def get_all_venues(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM venues")
        return cursor.fetchall()
