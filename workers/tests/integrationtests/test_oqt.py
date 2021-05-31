import asyncio
import unittest

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        dataset = "regions"
        feature_id = 31
        self.bpolys = asyncio.run(
            db_client.get_bpolys_from_db(dataset, feature_id, "ogc_fid")
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator_from_scratch(self):
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
    def test_create_indicator_from_database_invalid_dataset(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset="foo",
                    feature_id=31,
                )
            )

    def test_create_indicator_from_database_invalid_fid_field(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset="regions",
                    fid_field="foo",
                    feature_id=31,
                )
            )

    @oqt_vcr.use_cassette()
    def testCreateIndicatorFromDatabaseDefaultFidField(self):
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset="regions",
                feature_id=31,
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    # TODO:
    # def testCreateIndicatorFromDatabaseCustomFidField(self):
    #     indicator = asyncio.run(
    #         oqt.create_indicator(
    #             "GhsPopComparisonBuildings",
    #             "building_count",
    #             dataset="regions",
    #             fid_field="name",
    #             fid="Tun Borj Bourguiba",
    #         )
    #     )
    #     self.assertIsNotNone(indicator.result.label)
    #     self.assertIsNotNone(indicator.result.value)
    #     self.assertIsNotNone(indicator.result.description)
    #     self.assertIsNotNone(indicator.result.svg)

    def testCreateIndicatorFromDatabaseInvalidArguments(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset="regions",
                    feature_id=31,
                    bpolys=self.bpolys,
                )
            )

    @oqt_vcr.use_cassette()
    def test_create_report_from_scratch(self):
        report = asyncio.run(oqt.create_report("SimpleReport", bpolys=self.bpolys))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_from_database(self):
        report = asyncio.run(
            oqt.create_report("SimpleReport", dataset="regions", feature_id=31)
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
