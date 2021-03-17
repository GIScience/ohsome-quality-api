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
        """Test connection failure error due to wrong credentials"""
        env = "POSTGRES_PORT"  # Default if no custom DB credentials are set
        for var in (
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
        ):
            try:
                value = os.environ.pop(var)
                env = var
                break
            except KeyError:
                continue
        os.environ[env] = ""
        with self.assertRaises(OperationalError):
            PostgresDB()
        os.environ[env] = value


if __name__ == "__main__":
    unittest.main()
