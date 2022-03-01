import asyncio
import unittest

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)


class TestBaseIndicator(unittest.TestCase):
    def setUp(self):
        self.feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        self.layer_name = "building_count"

    def test_as_feature(self):
        indicator = GhsPopComparisonBuildings(
            feature=self.feature, layer_name=self.layer_name
        )

        feature = indicator.as_feature()
        self.assertTrue(feature.is_valid)
        for i in (
            "pop_count",
            "area",
            "pop_count_per_sqkm",
            "feature_count",
            "feature_count_per_sqkm",
        ):
            self.assertIn(i, feature["properties"]["data"].keys())

    def test_as_feature_flatten(self):
        indicator = GhsPopComparisonBuildings(
            feature=self.feature, layer_name=self.layer_name
        )
        feature = indicator.as_feature(flatten=True)
        self.assertTrue(feature.is_valid)
        for i in (
            "data.pop_count",
            "data.area",
            "data.pop_count_per_sqkm",
            "data.feature_count",
            "data.feature_count_per_sqkm",
        ):
            self.assertIn(i, feature["properties"].keys())

    def test_data_property(self):
        indicator = GhsPopComparisonBuildings(
            feature=self.feature, layer_name=self.layer_name
        )
        self.assertIsNotNone(indicator.data)
        for key in indicator.data.keys():
            self.assertNotIn(key, ("result", "metadata", "layer", "feature"))

    def test_attribution_class_property(self):
        self.assertIsNotNone(GhsPopComparisonBuildings.attribution())
        self.assertIsInstance(GhsPopComparisonBuildings.attribution(), str)
