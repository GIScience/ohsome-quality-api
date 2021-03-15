import os
import unittest

from psycopg2._psycopg import connection as psycopg_connection
from psycopg2._psycopg import cursor as psycopg_cursor
from psycopg2.errors import OperationalError

from ohsome_quality_analyst.geodatabase.auth import PostgresDB


class TestPostgres(unittest.TestCase):
    def test_connection(self):
        db_client = PostgresDB()
        self.assertIsInstance(db_client._connection, psycopg_connection)
        self.assertIsInstance(db_client._cursor, psycopg_cursor)

    def test_connection_fails(self):
        os.environ["POSTGRES_HOST"] = ""
        os.environ["POSTGRES_PORT"] = ""
        os.environ["POSTGRES_DB"] = ""
        os.environ["POSTGRES_USER"] = ""
        os.environ["POSTGRES_PASSWORD"] = ""
        with self.assertRaises(OperationalError):
            PostgresDB()
        os.environ.pop("POSTGRES_HOST")
        os.environ.pop("POSTGRES_PORT")
        os.environ.pop("POSTGRES_DB")
        os.environ.pop("POSTGRES_USER")
        os.environ.pop("POSTGRES_PASSWORD")


if __name__ == "__main__":
    unittest.main()
