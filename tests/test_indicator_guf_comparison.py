import os
import unittest

import geojson

from ohsome_quality_tool.oqt import get_dynamic_indicator


class TestGufComparisonIndicator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = "guf-comparison"
        self.layer_name = "building-area"

    def test_get_dynamic_indicator(self):
        """Test if dynamic indicator can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/antanarivo.geojson")
        with open(infile, "r") as file:
            bpolys = geojson.load(file)
        result, metadata = get_dynamic_indicator(
            indicator_name=self.indicator_name,
            bpolys=bpolys,
            layer_name=self.layer_name,
        )

        # check if result dict contains the right keys
        self.assertListEqual(list(result._fields), ["label", "value", "text", "svg"])


if __name__ == "__main__":
    unittest.main()
