import asyncio
import unittest

from asyncpg.exceptions import DataError, UndefinedColumnError, UndefinedTableError

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)

from .utils import oqt_vcr


class TestGeodatabase(unittest.TestCase):
    def setUp(self):
        self.dataset = "regions"
        self.feature_id = 11  # Algeria Touggourt
        self.fid_field = "ogc_fid"
        self.feature = asyncio.run(
            db_client.get_region_from_db(self.feature_id, self.fid_field)
        )

    def test_get_connection(self):
        async def _test_get_connection():
            async with db_client.get_connection() as conn:
                return await conn.fetchrow("SELECT 1")

        result = asyncio.run(_test_get_connection())
        self.assertEqual(result[0], 1)

    @oqt_vcr.use_cassette()
    def test_save_and_load(self):
        # TODO: split tests by functionality (load and safe),
        # but load test needs a saved indicator.
        # save
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count",
            feature=self.feature,
        )
        asyncio.run(self.indicator.preprocess())
        self.indicator.calculate()
        self.indicator.create_figure()
        asyncio.run(
            db_client.save_indicator_results(
                self.indicator, self.dataset, self.feature_id
            )
        )

        # load
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count", feature=self.feature
        )
        result = asyncio.run(
            db_client.load_indicator_results(
                self.indicator, self.dataset, self.feature_id
            )
        )
        self.assertTrue(result)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)

    def test_get_feature_ids(self):
        result = asyncio.run(db_client.get_feature_ids(self.dataset, self.fid_field))
        self.assertIsInstance(result, list)
        self.assertTrue(result)

        with self.assertRaises(UndefinedColumnError):
            asyncio.run(db_client.get_feature_ids(self.dataset, "foo"))

        with self.assertRaises(UndefinedTableError):
            asyncio.run(db_client.get_feature_ids("foo", self.fid_field))

    def test_get_area_of_bpolys(self):
        result = asyncio.run(db_client.get_area_of_bpolys(self.feature.geometry))
        self.assertIsInstance(result, float)

    def test_get_region_from_db(self):
        result = asyncio.run(
            db_client.get_region_from_db(self.feature_id, self.fid_field)
        )
        self.assertTrue(result.is_valid)  # GeoJSON object validation

        with self.assertRaises(UndefinedColumnError):
            asyncio.run(db_client.get_region_from_db(self.feature_id, "foo"))

        with self.assertRaises(DataError):
            asyncio.run(db_client.get_region_from_db("foo", self.fid_field))

    def test_get_available_regions(self):
        regions = asyncio.run(db_client.get_available_regions())
        self.assertTrue(regions.is_valid)

    def test_sanity_check_dataset(self):
        self.assertFalse(db_client.sanity_check_dataset("foo"))
        self.assertTrue(db_client.sanity_check_dataset(self.dataset))

    def test_sanity_check_fid_field(self):
        self.assertFalse(db_client.sanity_check_fid_field(self.dataset, "foo"))
        self.assertTrue(db_client.sanity_check_fid_field(self.dataset, self.fid_field))


if __name__ == "__main__":
    unittest.main()
