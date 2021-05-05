import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst import oqt

from .utils import oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    @oqt_vcr.use_cassette("test_oqt.json")
    def testCreateIndicatorFromScratch(self):
        # From scratch
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings", "building_count", bpolys=self.bpolys
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette("test_oqt.json")
    def testCreateIndicatorFromDatabase(self):
        # Invalid dataset name
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset="test_region",
                    feature_id=1,
                )
            )

        # Valid parameters
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset="test_regions",
                feature_id=3,
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    # TODO
    # @oqt_vcr.use_cassette("test_oqt.json")
    def testCreateReportFromScratch(self):
        report = asyncio.run(oqt.create_report("SimpleReport", self.bpolys))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette("test_oqt.json")
    def testCreateReportFromDatabase(self):
        report = asyncio.run(
            oqt.create_report("SimpleReport", dataset="test_regions", feature_id=3)
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
