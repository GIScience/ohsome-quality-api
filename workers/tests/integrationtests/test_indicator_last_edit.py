import os
import unittest

import geojson

from ohsome_quality_analyst.indicators.last_edit.indicator import LastEdit


class TestIndicatorLastEdit(unittest.TestCase):
    def test(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        indicator = LastEdit(bpolys=bpolys, layer_name="major_roads")
        indicator.preprocess()
        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    def test_more_edited_features_then_features(self):
        """It can happen that edited features includes deleted features."""
        indicator = LastEdit(
            layer_name="amenities", dataset="test_regions", feature_id=7
        )
        indicator.preprocess()
        self.assertLess(indicator.total_features, indicator.edited_features)
        self.assertEqual(indicator.share_edited_features, 100)


if __name__ == "__main__":
    unittest.main()
