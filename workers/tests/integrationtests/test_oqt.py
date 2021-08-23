import asyncio
import os
import unittest
from unittest import mock

import geojson

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import oqt_vcr


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestOqt(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"
        self.feature = asyncio.run(
            db_client.get_feature_from_db(self.dataset, feature_id=self.feature_id)
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator_feature(self):
        """Test creating indicator from scratch."""
        # From scratch
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings", "building_count", feature=self.feature
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
                    feature_id=self.feature_id,
                )
            )

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_invalid_fid_field(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator(
                    "GhsPopComparisonBuildings",
                    "building_count",
                    dataset=self.dataset,
                    feature_id=self.feature_id,
                    fid_field="foo",
                )
            )

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_default_fid_field(self):
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset=self.dataset,
                feature_id=self.feature_id,
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
                dataset=self.dataset,
                feature_id=self.feature_id,
                fid_field=self.fid_field,
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
                dataset=self.dataset,
                feature_id="Heidelberg",
                fid_field="name",
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_create_indicator_from_database_invalid_arguments(self):
        indicator = asyncio.run(
            oqt.create_indicator(
                "GhsPopComparisonBuildings",
                "building_count",
                dataset=self.dataset,
                feature_id=self.feature_id,
                feature=self.feature,
            )
        )
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_create_report_feature(self):
        report = asyncio.run(oqt.create_report("SimpleReport", feature=self.feature))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_default_fid_field(self):
        report = asyncio.run(
            oqt.create_report(
                "SimpleReport", dataset=self.dataset, feature_id=self.feature_id
            )
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_int(self):
        report = asyncio.run(
            oqt.create_report(
                "SimpleReport",
                dataset=self.dataset,
                feature_id=self.feature_id,
                fid_field=self.fid_field,
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
                dataset=self.dataset,
                feature_id="Heidelberg",  # equals ogc_fid 3
                fid_field="name",
            )
        )
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    @mock.patch("ohsome_quality_analyst.utils.definitions")
    def test_create_all_indicators(self, definitions_mock):
        definitions_mock.INDICATOR_LAYER = (
            ("GhsPopComparisonBuildings", "building_count"),
        )
        with mock.patch(
            "ohsome_quality_analyst.geodatabase.client.get_feature_ids",
            new_callable=AsyncMock,
        ) as get_feature_ids_mock:
            get_feature_ids_mock.return_value = ["3"]
            asyncio.run(oqt.create_all_indicators())

    def test_check_area_size(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "europe.geojson"
        )
        with open(path, "r") as f:
            feature = geojson.load(f)
        with self.assertRaises(ValueError):
            asyncio.run(oqt.check_area_size(feature.geometry))


if __name__ == "__main__":
    unittest.main()
