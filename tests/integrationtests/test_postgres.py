import asyncio
import unittest
from types import MappingProxyType
from unittest import mock

import asyncpg
import pytest

from ohsome_quality_api.geodatabase import client as pg_client

pytestmark = pytest.mark.skip("dependency on database setup.")


async def get_connection_context_manager():
    async with pg_client.get_connection() as conn:
        return type(conn)


class TestPostgres(unittest.TestCase):
    def test_connection(self):
        instance_type = asyncio.run(get_connection_context_manager())
        self.assertEqual(instance_type, asyncpg.connection.Connection)

    @mock.patch(
        "ohsome_quality_api.config.get_config",
    )
    def test_connection_fails(self, mock_get_config):
        """Test connection failure error due to wrong credentials"""
        mock_get_config.return_value = MappingProxyType(
            {
                "postgres_host": "foo",
                "postgres_port": "9999",
                "postgres_db": "bar",
                "postgres_user": "tis",
                "postgres_password": "fas",
            }
        )
        with self.assertRaises(OSError):
            asyncio.run(get_connection_context_manager())


if __name__ == "__main__":
    unittest.main()
