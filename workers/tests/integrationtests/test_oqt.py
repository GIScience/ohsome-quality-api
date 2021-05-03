import asyncio
import os
import unittest

import geojson
import vcr

from ohsome_quality_analyst import oqt

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_BASENAME = os.path.splitext(os.path.basename(__file__))[0]


class TestOqt(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
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

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
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
    # @vcr.use_cassette(
    #     os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    # )
    def testCreateReportFromScratch(self):
        report = asyncio.run(oqt.create_report("SimpleReport", self.bpolys))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def testCreateReportFromDatabase(self):
        report = asyncio.run(
            oqt.create_report("SimpleReport", dataset="test_regions", feature_id=3)
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
