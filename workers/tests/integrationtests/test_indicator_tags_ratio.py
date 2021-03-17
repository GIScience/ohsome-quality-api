import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.indicators.tags_ratio.indicator import TagsRatio


class TestIndicatorRatio(unittest.TestCase):
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

    def test_all_features_match(self):
        """It can happen that edited features includes deleted features"""
        indicator = TagsRatio(
            layer_name="jrc_health_count",
            dataset="test_regions",
            feature_id=8,
        )
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, indicator.count_match)

    def test_no_features(self):
        """Test area with no features"""
        indicator = TagsRatio(
            layer_name="jrc_health_count",
            dataset="test_regions",
            feature_id=2,
        )
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, 0)
        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)


if __name__ == "__main__":
    unittest.main()
