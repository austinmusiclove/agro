import sys
import logging
import pymysql
import json
import os

# rds settings
user_name = os.environ['USER_NAME']
password = os.environ['PASSWORD']
rds_proxy_host = os.environ['RDS_PROXY_HOST']
db_name = os.environ['DB_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create the database connection outside of the handler to allow connections to be
# re-used by subsequent function invocations.
try:
    connection = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit(1)

logger.info("SUCCESS: Connection to RDS for MySQL instance succeeded")

def get_staged_transactions_events(event, context):
    try:
        # Check if connection is still alive, reconnect if dead
        connection.ping(reconnect=True)

        with connection.cursor() as cursor:
            # 2. SQL Join to get staged transactions and their related events
            # We join 'events' twice: once for current_data and once for staged_data
            sql = """
                SELECT
                    st.*,
                    e_current.title as current_event_title,
                    e_current.venue_id as current_venue_id,
                    e_current.start_date as current_start_date,
                    e_staged.title as staged_event_title,
                    e_staged.venue_id as staged_venue_id,
                    e_staged.start_date as staged_start_date
                FROM staged_transactions st
                LEFT JOIN events e_current ON st.current_data_id = e_current.id
                LEFT JOIN events e_staged ON st.staged_data_id = e_staged.id
                WHERE st.target_table = 'events'
                AND st.status = 'pending-review';
            """

            cursor.execute(sql)
            records = cursor.fetchall()

            # 3. Handle data types (JSON/DateTime) for API Gateway response
            # Note: Decimals and DateTimes aren't naturally JSON serializable
            serialized_records = json.loads(json.dumps(records, default=str))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'event': json.dumps(event, default=str),
                'path': event.get('path'),
                'count': len(serialized_records),
                'transactions': serialized_records
            })
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
