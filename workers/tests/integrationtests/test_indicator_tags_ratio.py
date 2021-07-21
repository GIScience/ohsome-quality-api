import asyncio
import os
import unittest
from datetime import datetime

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.tags_ratio.indicator import TagsRatio

from .utils import oqt_vcr


class TestIndicatorRatio(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id=3, fid_field="ogc_fid"
            )
        )

    @oqt_vcr.use_cassette()
    def test(self):
        indicator = TagsRatio(
            feature=self.feature,
            layer_name="jrc_health_count",
        )
        asyncio.run(indicator.preprocess())
        self.assertIsNotNone(indicator.result.timestamp_osm)
        self.assertIsInstance(indicator.result.timestamp_osm, datetime)

        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_no_features(self):
        """Test area with no features"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = TagsRatio(layer_name="jrc_health_count", feature=feature)
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, 0)

        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)

    @oqt_vcr.use_cassette()
    def test_no_filter2(self):
        """Layer with no filter2 for ratio endpoint"""
        with self.assertRaises(ValueError):
            TagsRatio(layer_name="major_roads_length", feature=self.feature)


if __name__ == "__main__":
    unittest.main()
