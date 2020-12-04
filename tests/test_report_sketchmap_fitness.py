import os
import unittest

import geojson

from ohsome_quality_tool.oqt import get_dynamic_report


class TestSketchmapFitnessReport(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.report_name = "SKETCHMAP_FITNESS"

    def test_get_dynamic_report(self):
        """Test if dynamic report can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile, "r") as file:
            bpolys = geojson.load(file)

        result, indicators, metadata = get_dynamic_report(
            report_name=self.report_name, bpolys=bpolys
        )

        # check if result dict contains the right keys
        # check if result dict contains the right keys
        self.assertListEqual(list(result._fields), ["label", "value", "text"])


if __name__ == "__main__":
    unittest.main()
