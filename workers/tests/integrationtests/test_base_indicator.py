import asyncio
import unittest

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)


class TestBaseIndicator(unittest.TestCase):
    def test_as_feature(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id="3", fid_field="ogc_fid"
            )
        )
        indicator = GhsPopComparisonBuildings(
            feature=feature, layer_name="building_count"
        )

        feature = indicator.as_feature()
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
        feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id="3", fid_field="ogc_fid"
            )
        )
        indicator = GhsPopComparisonBuildings(
            feature=feature, layer_name="building_count"
        )
        self.assertIsNotNone(indicator.data)
        for key in indicator.data.keys():
            self.assertNotIn(key, ("result", "metadata", "layer", "feature"))
