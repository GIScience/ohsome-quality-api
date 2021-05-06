import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.tags_ratio.indicator import TagsRatio

from .utils import oqt_vcr


class TestIndicatorRatio(unittest.TestCase):
    @oqt_vcr.use_cassette()
    def test(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        indicator = TagsRatio(
            bpolys=bpolys,
            layer_name="jrc_health_count",
        )
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_all_features_match(self):
        """Ratio should be 1.0 when all features match expected tags"""
        layer_name = "jrc_health_count"
        dataset = "test_regions"
        feature_id = 8
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        indicator = TagsRatio(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, indicator.count_match)
        self.assertEqual(indicator.ratio, 1.0)
        indicator.calculate()

    @oqt_vcr.use_cassette()
    def test_no_features(self):
        """Test area with no features"""
        layer_name = "jrc_health_count"
        dataset = "test_regions"
        feature_id = 2
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        indicator = TagsRatio(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, 0)
        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)

    @oqt_vcr.use_cassette()
    def test_no_filter2(self):
        """Layer with no filter2 for ratio endpoint"""
        layer_name = "major_roads"
        dataset = "test_regions"
        feature_id = 2
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        indicator = TagsRatio(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        self.assertIsNone(indicator.count_all)
        indicator.calculate()


if __name__ == "__main__":
    unittest.main()
