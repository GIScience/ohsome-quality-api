import asyncio
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.utils.helper import datetime_to_isostring_timestamp


class TestBaseIndicator(unittest.TestCase):
    def test_geo_interface(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id="3", fid_field="ogc_fid"
            )
        )
        indicator = GhsPopComparisonBuildings(
            feature=feature, layer_name="building_count"
        )

        feature = geojson.dumps(indicator, default=datetime_to_isostring_timestamp)
        self.assertTrue(geojson.loads(feature).is_valid)

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
        keys = indicator.data.keys()
        for key in keys:
            self.assertNotIn(
                key, ("result", "metadata", "layer", "feature", "__geo_interface__")
            )
