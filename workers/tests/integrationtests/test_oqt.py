import asyncio
import os
import unittest
from unittest import mock

import geojson

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorDatabase,
    ReportBpolys,
    ReportDatabase,
)
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import AsyncMock, oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.name = "GhsPopComparisonBuildings"
        self.report_name = "SimpleReport"
        self.layer_name = "building_count"
        self.dataset = "regions"
        self.feature_id = "3"
        self.fid_field = "ogc_fid"
        self.feature = asyncio.run(
            db_client.get_feature_from_db(self.dataset, feature_id=self.feature_id)
        )

    def run_tests(self, indicator):
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_create_indicator_bpolys(self):
        """Test creating indicator from scratch."""
        parameters = IndicatorBpolys(
            name=self.name,
            layerName=self.layer_name,
            bpolys=self.feature,
        )
        indicator = asyncio.run(oqt.create_indicator(parameters))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_default_fid_field(self):
        parameters = IndicatorDatabase(
            name=self.name,
            layerName=self.layer_name,
            dataset=self.dataset,
            featureId=self.feature_id,
        )
        indicator = asyncio.run(oqt.create_indicator(parameters))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_custom_fid_field_int(self):
        parameters = IndicatorDatabase(
            name=self.name,
            layerName=self.layer_name,
            dataset=self.dataset,
            featureId=self.feature_id,
            fidField=self.fid_field,
        )
        indicator = asyncio.run(oqt.create_indicator(parameters))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_custom_fid_field_str(self):
        parameters = IndicatorDatabase(
            name=self.name,
            layerName=self.layer_name,
            dataset=self.dataset,
            featureId="Heidelberg",
            fidField="name",
        )
        indicator = asyncio.run(oqt.create_indicator(parameters))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_report_bpolys(self):
        """Test creating indicator from scratch using the 'bpolys'parameters ."""
        parameters = ReportBpolys(
            name=self.report_name,
            bpolys=self.feature,
        )
        report = asyncio.run(oqt.create_report(parameters))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_default_fid_field(self):
        parameters = ReportDatabase(
            name=self.report_name,
            dataset=self.dataset,
            featureId=self.feature_id,
        )
        report = asyncio.run(oqt.create_report(parameters))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_int(self):
        parameters = ReportDatabase(
            name=self.report_name,
            dataset=self.dataset,
            featureId=self.feature_id,
            fidField=self.fid_field,
        )
        report = asyncio.run(oqt.create_report(parameters))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_str(self):
        parameters = ReportDatabase(
            name=self.report_name,
            dataset=self.dataset,
            featureId="Heidelberg",
            fidField="name",
        )
        report = asyncio.run(oqt.create_report(parameters))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)

    @mock.patch(
        "ohsome_quality_analyst.oqt.INDICATOR_LAYER",
        (
            ("GhsPopComparisonBuildings", "building_count"),
            ("GhsPopComparisonRoads", "major_roads_length"),
        ),
    )
    @oqt_vcr.use_cassette()
    def test_create_all_indicators(self):
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
