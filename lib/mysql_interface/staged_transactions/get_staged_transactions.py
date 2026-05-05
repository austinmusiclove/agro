from lib.mysql_interface.events import events
from lib.mysql_interface.venues import venues


def get_staged_transactions(connector, target_table):
    sql = """
        SELECT
            st.*,
            e_current.title as current_event_title,
            e_current.venue_id as current_venue_id,
            e_current.start_date as current_start_date,
            e_staged.title as staged_event_title,
            e_staged.venue_id as staged_venue_id,
            e_staged.start_date as staged_start_date,
            vs.name as staged_venue_name,
            vc.name as current_venue_name
        FROM staged_transactions st
        LEFT JOIN events e_current ON st.current_data_id = e_current.id
        LEFT JOIN events e_staged ON st.staged_data_id = e_staged.id
        LEFT JOIN venues vs ON e_staged.venue_id = vs.id
        LEFT JOIN venues vc ON e_current.venue_id = vc.id
        WHERE st.target_table = ?
        AND st.status = 'pending-review';
    """
    return connector.execute_query(sql, [target_table])
