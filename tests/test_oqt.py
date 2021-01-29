import os
import unittest

import geojson

from ohsome_quality_tool import oqt


class TestOqt(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    def testCreateIndicatorFromScratch(self):
        # From scratch
        indicator = oqt.create_indicator(
            "GhsPopComparison", "building_count", bpolys=self.bpolys
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    def testCreateIndicatorFromDatabase(self):
        # Invalid dataset name
        with self.assertRaises(ValueError):
            oqt.create_indicator(
                "GhsPopComparison",
                "building_count",
                dataset="test_region",
                feature_id=1,
            )

        indicator = oqt.create_indicator(
            "GhsPopComparison", "building_count", dataset="test_regions", feature_id=3
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    def testCreateReport(self):
        report = oqt.create_report("SimpleReport", self.bpolys)
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
