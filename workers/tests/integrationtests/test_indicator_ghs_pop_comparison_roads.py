import asyncio
import unittest

from asyncpg import Record

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_roads.indicator import (
    GhsPopComparisonRoads,
)


class TestIndicatorGhsPopComparisonRoads(unittest.TestCase):
    def setUp(self):
        dataset = "regions"
        feature_id = 3  # Heidelberg
        bpolys = asyncio.run(
            db_client.get_bpolys_from_db(dataset, feature_id, "ogc_fid")
        )
        self.indicator = GhsPopComparisonRoads(
            bpolys=bpolys, layer_name="major_roads_length"
        )

    def test(self):
        asyncio.run(self.indicator.preprocess())
        self.assertIsNotNone(self.indicator.pop_count)
        self.assertIsNotNone(self.indicator.area)
        self.assertIsNotNone(self.indicator.feature_length)
        self.assertIsNotNone(self.indicator.feature_length_per_sqkm)
        self.assertIsNotNone(self.indicator.pop_count_per_sqkm)

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)

        self.indicator.create_figure()
        self.assertIsNotNone(self.indicator.result.svg)

    def test_get_zonal_stats_population(self):
        result = asyncio.run(
            self.indicator.get_zonal_stats_population(self.indicator.bpolys)
        )
        self.assertIsInstance(result, Record)


if __name__ == "__main__":
    unittest.main()
