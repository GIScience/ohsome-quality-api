import os
import unittest

import geojson

from ohsome_quality_tool.oqt import get_dynamic_indicator
from ohsome_quality_tool.utils.definitions import Indicators


class TestLastEditIndicator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = Indicators.LAST_EDIT.name

    def test_get_dynamic_indicator(self):
        """Test if dynamic indicator can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile, "r") as file:
            bpolys = geojson.load(file)
        result, metadata = get_dynamic_indicator(
            indicator_name=self.indicator_name, bpolys=bpolys
        )

        # check if result dict contains the right keys
        self.assertListEqual(list(result._fields), ["label", "value", "text", "svg"])


if __name__ == "__main__":
    unittest.main()
