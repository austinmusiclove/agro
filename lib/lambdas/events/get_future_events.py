import json
import math


def get_future_events(mysql_interface, logger, venue_id=None, page=1, page_size=20):
    try:
        offset = (page - 1) * page_size
        events_list = mysql_interface.get_future_events_by_venue(venue_id, limit=page_size, offset=offset)
        total = mysql_interface.get_future_events_count(venue_id)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'count': len(events_list),
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': math.ceil(total / page_size) if total else 0,
                'venue_id': venue_id,
                'events': events_list
            })
        }

    except Exception as e:
        logger.error(f"Error fetching future events: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
