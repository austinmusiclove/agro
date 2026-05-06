from lib.helpers.helper import format_time


def get_event_by_id(connector, event_id):
    sql = """
        SELECT e.*, v.name as venue_name
        FROM events e
        LEFT JOIN venues v ON e.venue_id = v.id
        WHERE e.id = ?
    """
    results = connector.execute_query(sql, [event_id])
    return results[0] if results else None

def get_future_events_by_venue(connector, venue_id=None, limit=None, offset=None):
    venue_clause = "venue_id = ? AND " if venue_id is not None else ""
    limit_clause = "LIMIT ? OFFSET ?" if limit is not None else ""
    sql = f"""SELECT id, title, venue_id, start_date, end_date, start_time, end_time, ages, price_range, event_page_url, ticket_url, image_url
              FROM events
              WHERE {venue_clause}start_date >= CURDATE() - INTERVAL 1 DAY AND status = 'published'
              ORDER BY start_date ASC, start_time ASC
              {limit_clause}"""
    params = [venue_id] if venue_id is not None else []
    if limit is not None:
        params.extend([limit, offset or 0])
    return connector.execute_query(sql, params)


def get_future_events_count(connector, venue_id=None):
    venue_clause = "WHERE venue_id = ? AND " if venue_id is not None else "WHERE "
    sql = f"""SELECT COUNT(*) as total
              FROM events
              {venue_clause}start_date >= CURDATE() - INTERVAL 1 DAY AND status = 'published'"""
    params = [venue_id] if venue_id is not None else []
    result = connector.execute_query(sql, params)
    return result[0]["total"] if result else 0


def insert_event(connector, event_data):
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
        event_data.get("price_range"),
        event_data.get("status", "staged"),
        event_data.get("data_source"),
        event_data.get("event_page_url"),
        event_data.get("ticket_url"),
        event_data.get("image_ref"),
        event_data.get("image_url"),
    ]

    placeholders = ", ".join(["?"] * len(columns))
    columns_str = ", ".join(columns)

    query = f"INSERT INTO events ({columns_str}) VALUES ({placeholders})"
    return connector.execute_insert(query, values)


def update_event(connector, event_id, event_data):
    # Remove fields that shouldn't be updated
    fields_to_update = {k: v for k, v in event_data.items()
                       if k not in ['id', 'created_at', 'updated_at']}

    if not fields_to_update:
        return 0

    set_clause = ", ".join([f"{col} = ?" for col in fields_to_update.keys()])
    values = list(fields_to_update.values()) + [event_id]

    query = f"UPDATE events SET {set_clause} WHERE id = ?"
    return connector.execute_update(query, values)
