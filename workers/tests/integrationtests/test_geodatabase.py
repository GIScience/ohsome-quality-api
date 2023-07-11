import asyncio
import os
import unittest

import geojson
import pytest

import ohsome_quality_analyst.geodatabase.client as db_client
from tests.conftest import FIXTURE_DIR
from tests.integrationtests.utils import get_geojson_fixture

pytestmark = pytest.mark.skip("dependency on database setup.")


class TestGeodatabase(unittest.TestCase):
    def setUp(self):
        path = os.path.join(
            FIXTURE_DIR,
            "feature-germany-heidelberg.geojson",
        )
        with open(path, "r") as f:
            self.feature = geojson.load(f)

    def test_get_connection(self):
        async def _test_get_connection():
            async with db_client.get_connection() as conn:
                return await conn.fetchrow("SELECT 1")

        result = asyncio.run(_test_get_connection())
        self.assertEqual(result[0], 1)

    def test_get_shdi_single_intersection_feature(self):
        """Input geometry intersects only with one SHDI region."""
        result = asyncio.run(db_client.get_shdi(self.feature))
        self.assertIsInstance(result[0]["shdi"], float)
        self.assertLessEqual(result[0]["shdi"], 1.0)
        self.assertEqual(len(result), 1)

    def test_get_shdi_single_intersection_featurecollection(self):
        featurecollection = get_geojson_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson"
        )
        result = asyncio.run(db_client.get_shdi(featurecollection))
        self.assertIsInstance(result[0]["shdi"], float)
        self.assertLessEqual(result[0]["shdi"], 1.0)
        self.assertIsInstance(result[1]["shdi"], float)
        self.assertLessEqual(result[1]["shdi"], 1.0)
        self.assertEqual(len(result), 2)

    def test_get_shdi_type_error(self):
        with self.assertRaises(TypeError):
            asyncio.run(db_client.get_shdi(self.feature.geometry))

    # Note: This test can only be executed if the whole SHDI is in the database.
    # def test_get_shdi_multiple_intersections(self):
    #     """Input geometry intersects with multiple SHDI-regions."""
    #     geom = geojson.Polygon(
    #         [
    #             [
    #                 [13.610687255859375, 48.671919512374565],
    #                 [14.0350341796875, 48.671919512374565],
    #                 [14.0350341796875, 48.865618158309374],
    #                 [13.610687255859375, 48.865618158309374],
    #                 [13.610687255859375, 48.671919512374565],
    #             ]
    #         ],
    #     )
    #     result = asyncio.run(db_client.get_shdi(geom))
    #     self.assertIsInstance(result[0]["shdi"], float)
    #     self.assertLessEqual(result[0]["shdi"], 1.0)


if __name__ == "__main__":
    unittest.main()
