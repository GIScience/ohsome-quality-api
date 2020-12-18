import os
import unittest

import geojson

from ohsome_quality_tool.oqt import get_dynamic_report, get_static_report


class TestRemoteMappingLevelOneReport(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.report_name = "remote-mapping-level-one"
        self.dataset = "test-regions"
        self.feature_id = 1

    def test_get_dynamic_report(self):
        """Test if dynamic report can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        with open(infile, "r") as file:
            bpolys = geojson.load(file)

        result, indicators, metadata = get_dynamic_report(
            report_name=self.report_name, bpolys=bpolys
        )

        # check if result dict contains the right keys
        self.assertListEqual(list(result._fields), ["label", "value", "text"])

    def test_get_static_report(self):
        """Test if dynamic report can be calculated."""
        result, indicators, metadata = get_static_report(
            report_name=self.report_name,
            dataset=self.dataset,
            feature_id=self.feature_id,
        )

        # check if result dict contains the right keys
        # check if result dict contains the right keys
        self.assertListEqual(list(result._fields), ["label", "value", "text"])


if __name__ == "__main__":
    unittest.main()
