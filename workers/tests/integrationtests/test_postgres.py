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
        env_backup = {}
        env_names = [
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
        ]
        for env_name in env_names:
            try:
                value = os.environ.pop(env_name)
                print(value)
                env_backup[env_name] = value
            except KeyError:
                pass
            os.environ[env_name] = ""
        with self.assertRaises(OperationalError):
            PostgresDB()
        for env_name in env_names:
            if env_name in env_backup:
                os.environ[env_name] = env_backup[env_name]
            else:
                os.environ.pop(env_name)


if __name__ == "__main__":
    unittest.main()
