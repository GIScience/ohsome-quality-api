import asyncio
import os
import unittest
from datetime import datetime

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.currentness.indicator import Currentness

from .utils import get_layer_fixture, oqt_vcr


class TestIndicatorCurrentness(unittest.TestCase):
    @oqt_vcr.use_cassette()
    def test(self):
        # Heidelberg
        feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )

        indicator = Currentness(
            feature=feature,
            layer=get_layer_fixture("major_roads_count"),
        )
        self.assertIsNotNone(indicator.attribution())

        asyncio.run(indicator.preprocess())
        self.assertIsInstance(indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(indicator.result.timestamp_oqt, datetime)
        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_no_amenities(self):
        """Test area with no amenities"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = Currentness(feature=feature, layer=get_layer_fixture("amenities"))
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.element_count, 0)

        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)


if __name__ == "__main__":
    unittest.main()
