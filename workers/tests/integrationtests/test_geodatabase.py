import asyncio
import os
import unittest

import geojson
from asyncpg.exceptions import DataError, UndefinedColumnError

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)

from .utils import oqt_vcr


class TestGeodatabase(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    @oqt_vcr.use_cassette()
    def test_save_and_load(self):
        # TODO: split tests by functionality (load and safe),
        # but load test needs a saved indicator.
        dataset = "regions"
        feature_id = 2
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        # save
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count",
            bpolys=bpolys,
        )
        asyncio.run(self.indicator.preprocess())
        self.indicator.calculate()
        self.indicator.create_figure()
        asyncio.run(
            db_client.save_indicator_results(self.indicator, dataset, feature_id)
        )

        # load
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count", bpolys=bpolys
        )
        result = asyncio.run(
            db_client.load_indicator_results(self.indicator, dataset, feature_id)
        )
        self.assertTrue(result)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_get_ids(self):
        result = asyncio.run(db_client.get_ids("regions", "fid"))
        self.assertIsInstance(result, list)

    @oqt_vcr.use_cassette()
    def test_get_area_of_bpoly(self):
        result = asyncio.run(db_client.get_area_of_bpoly(self.bpolys))
        self.assertIsInstance(result, float)

    @oqt_vcr.use_cassette()
    def test_get_bpoly_from_db(self):
        result = asyncio.run(
            db_client.get_bpoly_from_db("regions", 3, id_field="ogc_fid")
        )
        self.assertTrue(result.is_valid)  # GeoJSON object validation

        with self.assertRaises(UndefinedColumnError):
            asyncio.run(db_client.get_bpoly_from_db("regions", 3, id_field="foo"))

        with self.assertRaises(DataError):
            asyncio.run(db_client.get_bpoly_from_db("regions", "3", id_field="ogc_fid"))

    def test_get_available_regions(self):
        regions = asyncio.run(db_client.get_available_regions())
        self.assertTrue(regions.is_valid)


if __name__ == "__main__":
    unittest.main()
