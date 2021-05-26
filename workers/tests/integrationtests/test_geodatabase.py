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
        self.fid = 2
        self.bpoly = asyncio.run(
            db_client.get_bpoly_from_db(self.dataset, self.fid, "ogc_fid")
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
            bpolys=self.bpoly,
        )
        asyncio.run(self.indicator.preprocess())
        self.indicator.calculate()
        self.indicator.create_figure()
        asyncio.run(
            db_client.save_indicator_results(self.indicator, self.dataset, self.fid)
        )

        # load
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count", bpolys=self.bpoly
        )
        result = asyncio.run(
            db_client.load_indicator_results(self.indicator, self.dataset, self.fid)
        )
        self.assertTrue(result)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)

    def test_get_fids(self):
        result = asyncio.run(db_client.get_fids("regions", "ogc_fid"))
        self.assertIsInstance(result, list)
        self.assertTrue(result)

        with self.assertRaises(UndefinedColumnError):
            asyncio.run(db_client.get_fids("regions", "foo"))

        with self.assertRaises(UndefinedTableError):
            asyncio.run(db_client.get_fids("foo", "ogc_fid"))

    def test_get_area_of_bpoly(self):
        result = asyncio.run(db_client.get_area_of_bpoly(self.bpoly))
        self.assertIsInstance(result, float)

    def test_get_bpoly_from_db(self):
        result = asyncio.run(
            db_client.get_bpoly_from_db(self.dataset, self.fid, fid_field="ogc_fid")
        )
        self.assertTrue(result.is_valid)  # GeoJSON object validation

        with self.assertRaises(UndefinedColumnError):
            asyncio.run(
                db_client.get_bpoly_from_db(self.dataset, self.fid, fid_field="foo")
            )

        with self.assertRaises(DataError):
            asyncio.run(
                db_client.get_bpoly_from_db(self.dataset, "foo", fid_field="ogc_fid")
            )

        with self.assertRaises(UndefinedTableError):
            asyncio.run(
                db_client.get_bpoly_from_db("foo", self.fid, fid_field="ogc_fid")
            )

    def test_get_available_regions(self):
        regions = asyncio.run(db_client.get_available_regions())
        self.assertTrue(regions.is_valid)


if __name__ == "__main__":
    unittest.main()
