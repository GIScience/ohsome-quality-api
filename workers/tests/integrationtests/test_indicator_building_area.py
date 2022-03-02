import asyncio
import unittest
from datetime import datetime

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.building_area.indicator import BuildingArea

from .utils import oqt_vcr


class TestIndicatorBuildingArea(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        self.layer_name = "building_area"
        self.indicator = BuildingArea(feature=self.feature, layer_name=self.layer_name)

    @oqt_vcr.use_cassette()
    def test(self):
        asyncio.run(self.indicator.preprocess())
        self.assertIsNotNone(self.indicator.area)
        self.assertIsNotNone(self.indicator.building_area)
        self.assertIsInstance(self.indicator.result.timestamp_osm, datetime)

        self.assertIsNotNone(self.indicator.attrdict["ghspop"])
        self.assertIsNotNone(self.indicator.attrdict["ghspop_density_per_sqkm"])
        self.assertIsNotNone(self.indicator.attrdict["water"])
        self.assertIsNotNone(self.indicator.attrdict["very_low_rural"])
        self.assertIsNotNone(self.indicator.attrdict["low_rural"])
        self.assertIsNotNone(self.indicator.attrdict["rural_cluster"])
        self.assertIsNotNone(self.indicator.attrdict["suburban"])
        self.assertIsNotNone(self.indicator.attrdict["semi_dense_urban_cluster"])
        self.assertIsNotNone(self.indicator.attrdict["dense_urban_cluster"])
        self.assertIsNotNone(self.indicator.attrdict["urban_centre"])
        self.assertIsNotNone(self.indicator.attrdict["shdi_mean"])
        self.assertIsNotNone(self.indicator.attrdict["vnl_sum"])
        self.assertLessEqual(self.indicator.attrdict["urban_centre"], 1)
        self.assertGreaterEqual(self.indicator.attrdict["urban_centre"], 0)

        self.assertRaises(KeyError, lambda: self.indicator.attrdict["some_random_key"])

        """self.assertIsNotNone(self.indicator.feature_count)
        self.assertIsNotNone(self.indicator.feature_count_per_sqkm)
        self.assertIsNotNone(self.indicator.pop_count_per_sqkm)
        self.assertIsNotNone(self.indicator.attribution())

        self.assertIsInstance(self.indicator.result.timestamp_oqt, datetime)

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)

        self.indicator.create_figure()
        self.assertIsNotNone(self.indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_get_zonal_stats_population(self):
        result = asyncio.run(self.indicator.get_zonal_stats_population())
        self.assertIsInstance(result, Record)"""

    # TODO test other functions


if __name__ == "__main__":
    unittest.main()
