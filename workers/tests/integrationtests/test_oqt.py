import asyncio
import unittest

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        dataset = "regions"
        feature_id = 31
        fid_field = "ogc_fid"
        self.bpolys = asyncio.run(
            db_client.get_bpolys_from_db(dataset, feature_id, fid_field)
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator_bpolys(self):
        """Test creating indicator from scratch."""
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
    def test_create_indicator_invalid_dataset(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset="foo",
                    feature_id=3,
                )
            )

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_invalid_fid_field(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset="regions",
                    fid_field="foo",
                    feature_id=3,
                )
            )

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_default_fid_field(self):
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset="regions",
                feature_id=3,
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_custom_fid_field_int(self):
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset="regions",
                feature_id=3,
                fid_field="ogc_fid",
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_custom_fid_field_str(self):
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset="regions",
                feature_id="Alger Kenadsa medium",
                fid_field="name",
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_create_indicator_from_database_invalid_arguments(self):
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
    def test_create_report_bpolys(self):
        report = asyncio.run(oqt.create_report("SimpleReport", bpolys=self.bpolys))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_default_fid_field(self):
        report = asyncio.run(
            oqt.create_report("SimpleReport", dataset="regions", feature_id=31)
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_int(self):
        report = asyncio.run(
            oqt.create_report(
                "SimpleReport", dataset="regions", feature_id=31, fid_field="ogc_fid"
            )
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_str(self):
        report = asyncio.run(
            oqt.create_report(
                "SimpleReport",
                dataset="regions",
                feature_id="Alger Kenadsa medium",  # equals ogc_fid 3
                fid_field="name",
            )
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
