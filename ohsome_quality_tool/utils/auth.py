import psycopg2

from ohsome_quality_tool.utils.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


class postgresDB(object):
    """Helper calss for Postgres interactions"""

    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = psycopg2.connect(
            database=POSTGRES_DB,
            host=POSTGRES_HOST,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
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
