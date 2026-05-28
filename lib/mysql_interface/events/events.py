from lib.helpers.helper import format_time

EVENT_COLUMNS = [
    "title", "venue_id", "start_date", "end_date", "start_time", "end_time",
    "ages", "price_range", "status", "event_page_url", "ticket_url", "image_url",
    "data_source", "event_list_html_hash", "event_list_markdown_hash",
    "event_page_html_hash", "event_page_markdown_hash",
    "event_list_screenshot", "event_page_screenshot", "page_schema",
    "description",
]

EVENT_COLUMN_MAX_LENGTHS = {
    "title": 255,
    "ages": 50,
    "price_range": 100,
    "data_source": 100,
}


def _truncate(value, max_length):
    if isinstance(value, str) and max_length:
        return value[:max_length]
    return value


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
    sql = f"""SELECT e.id, e.title, e.venue_id, e.start_date, e.end_date, e.start_time, e.end_time, e.ages, e.price_range, e.event_page_url, e.ticket_url, e.image_url, e.description, e.status, v.name as venue_name
              FROM events e
              LEFT JOIN venues v ON e.venue_id = v.id
              WHERE {venue_clause}start_date >= CURDATE() - INTERVAL 1 DAY AND status = 'published'
              ORDER BY e.start_date ASC, e.start_time ASC, e.id ASC
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
    columns = EVENT_COLUMNS[:]
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
        event_data.get("event_page_url"),
        event_data.get("ticket_url"),
        event_data.get("image_url"),
        event_data.get("data_source"),
        event_data.get("event_list_html_hash"),
        event_data.get("event_list_markdown_hash"),
        event_data.get("event_page_html_hash"),
        event_data.get("event_page_markdown_hash"),
        event_data.get("event_list_screenshot"),
        event_data.get("event_page_screenshot"),
        event_data.get("page_schema"),
        event_data.get("description"),
    ]

    values = [
        _truncate(v, EVENT_COLUMN_MAX_LENGTHS.get(col))
        for col, v in zip(columns, values)
    ]

    placeholders = ", ".join(["?"] * len(columns))
    columns_str = ", ".join(columns)

    query = f"INSERT INTO events ({columns_str}) VALUES ({placeholders})"
    return connector.execute_insert(query, values)


def get_event_by_event_page_url(connector, event_page_url):
    sql = """
        SELECT * FROM events
        WHERE event_page_url = ?
        AND status = 'published'
        LIMIT 1
    """
    results = connector.execute_query(sql, [event_page_url])
    return results[0] if results else None


def update_event(connector, event_id, event_data):
    fields_to_update = {k: v for k, v in event_data.items()
                        if k in EVENT_COLUMNS}

    if not fields_to_update:
        return 0

    fields_to_update = {
        k: _truncate(v, EVENT_COLUMN_MAX_LENGTHS.get(k))
        for k, v in fields_to_update.items()
    }

    set_clause = ", ".join([f"{col} = ?" for col in fields_to_update.keys()])
    values = list(fields_to_update.values()) + [event_id]

    query = f"UPDATE events SET {set_clause} WHERE id = ?"
    return connector.execute_update(query, values)


def publish_event_from_schema(connector, schema_data, context_event):
    event_data = {
        "title": schema_data.get("title") or context_event.get("title"),
        "venue_id": context_event.get("venue_id"),
        "start_date": schema_data.get("start_date"),
        "end_date": schema_data.get("end_date"),
        "start_time": schema_data.get("start_time"),
        "end_time": schema_data.get("end_time"),
        "image_url": schema_data.get("image_url"),
        "price_range": schema_data.get("price_range"),
        "event_page_url": context_event.get("event_page_url"),
        "ticket_url": schema_data.get("ticket_url"),
        "data_source": context_event.get("data_source"),
        "status": "published",
        "page_schema": schema_data.get("page_schema"),
        "description": schema_data.get("description"),
    }

    return insert_event(connector, event_data)
