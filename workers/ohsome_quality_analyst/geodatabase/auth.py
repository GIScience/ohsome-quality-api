"""Handle Postgres database connection and interactions"""

import os
from typing import Iterable, TextIO, Union

import psycopg2

POSTGRES_SCHEMA = os.getenv("POSTGRES_SCHEMA", default="public")


class PostgresDB(object):
    def __init__(self):
        self._connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", default="localhost"),
            port=os.getenv("POSTGRES_PORT", default=5445),
            database=os.getenv("POSTGRES_DB", default="oqt"),
            user=os.getenv("POSTGRES_USER", default="oqt"),
            password=os.getenv("POSTGRES_PASSWORD", default="oqt"),
        )
        self._cursor = self._connection.cursor()

    def query(self, query: str, data=None):
        self._cursor.execute(query, data)
        self._connection.commit()

    def copy_from(self, file: TextIO, table: str, columns: Iterable = None):
        self._cursor.copy_from(file, table, columns=columns)
        self._connection.commit()

    def copy_expert(self, sql: str, file: TextIO):
        self._cursor.copy_expert(sql, file)
        self._connection.commit()

    def retr_query(self, query: str, data: Union[tuple, dict] = None):
        self._cursor.execute(query, data)
        content = self._cursor.fetchall()
        self._connection.commit()
        return content

    def __del__(self):
        try:
            self._cursor.close()
            self._connection.close()
        except AttributeError:
            pass
