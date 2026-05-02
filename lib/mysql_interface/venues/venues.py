def get_venue_by_id(connector, venue_id):
    sql = "SELECT * FROM venues WHERE id = ?"
    results = connector.execute_query(sql, [venue_id])
    return results[0] if results else None


def get_all_venues(connector):
    sql = "SELECT * FROM venues"
    return connector.execute_query(sql)
