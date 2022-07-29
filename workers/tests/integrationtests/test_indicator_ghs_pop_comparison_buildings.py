import asyncio
import unittest
from datetime import datetime

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)

from .utils import get_layer_fixture, oqt_vcr


class TestIndicatorGhsPopComparisonBuildings(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        layer = get_layer_fixture("building_count")
        self.indicator = GhsPopComparisonBuildings(feature=feature, layer=layer)

    @oqt_vcr.use_cassette()
    def test(self):
        asyncio.run(self.indicator.preprocess())
        self.assertIsNotNone(self.indicator.pop_count)
        self.assertIsNotNone(self.indicator.area)
        self.assertIsNotNone(self.indicator.feature_count)
        self.assertIsNotNone(self.indicator.pop_count_per_sqkm)
        self.assertIsNotNone(self.indicator.attribution())
        self.assertIsInstance(self.indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(self.indicator.result.timestamp_oqt, datetime)

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)

        self.indicator.create_figure()
        self.assertIsNotNone(self.indicator.result.svg)


if __name__ == "__main__":
    unittest.main()
