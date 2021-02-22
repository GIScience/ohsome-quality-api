import os

import psycopg2

POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", default="public")


class PostgresDB(object):
    """Helper class for Postgres interactions"""

    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", default="localhost"),
            port=os.getenv("POSTGRES_PORT", default=5445),
            database=os.getenv("POSTGRES_DB", default="oqt"),
            user=os.getenv("POSTGRES_USER", default="oqt"),
            password=os.getenv("POSTGRES_PASSWORD", default="oqt"),
        )

    def query(self, query, data=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_from(self, f, table, columns=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_from(f, table, columns=columns)
        self._db_connection.commit()
        self._db_cur.close()

    def copy_expert(self, sql, file):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.copy_expert(sql, file)
        self._db_connection.commit()
        self._db_cur.close()

    def retr_query(self, query, data=None):
        self._db_cur = self._db_connection.cursor()
        self._db_cur.execute(query, data)
        content = self._db_cur.fetchall()
        self._db_connection.commit()
        self._db_cur.close()
        return content

    def __del__(self):
        self._db_connection.close()
