import pprint
from korben import config
from korben.services import db

odata_connection = db.poll_for_connection(config.database_odata_url)
django_connection = db.poll_for_connection(config.django_database_url)


COUNT_ALL_SQL = '''
ANALYZE;
SELECT relname, n_live_tup
        FROM pg_stat_user_tables
        WHERE n_live_tup > 0
        ORDER BY n_live_tup DESC;
'''

for connection in (odata_connection, django_connection):
    result = connection.execute(COUNT_ALL_SQL).fetchall()
    pprint.pprint(result)
