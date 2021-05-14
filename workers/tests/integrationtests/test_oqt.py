import asyncio
import unittest

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        dataset = "regions"
        feature_id = 31
        self.bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

    @oqt_vcr.use_cassette()
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

    @oqt_vcr.use_cassette()
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
                dataset="regions",
                feature_id=4,
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def testCreateReportFromScratch(self):
        report = asyncio.run(oqt.create_report("SimpleReport", self.bpolys))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def testCreateReportFromDatabase(self):
        report = asyncio.run(
            oqt.create_report("SimpleReport", dataset="regions", feature_id=3)
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
