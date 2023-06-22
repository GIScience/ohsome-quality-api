import asyncio
import os
import unittest
from unittest import mock

import geojson

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorData,
    IndicatorDatabase,
    ReportBpolys,
    ReportDatabase,
)
from ohsome_quality_analyst.geodatabase import client as db_client
from tests.integrationtests.utils import get_geojson_fixture

from .utils import AsyncMock, oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.indicator_name = "minimal"
        self.report_name = "minimal"
        self.topic_key = "minimal"
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
        parameters = IndicatorBpolys(topic=self.topic_key, bpolys=self.feature)
        indicator = asyncio.run(oqt.create_indicator(parameters, self.indicator_name))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_default_fid_field(self):
        parameters = IndicatorDatabase(
            topic=self.topic_key,
            dataset=self.dataset,
            feature_id=self.feature_id,
        )
        indicator = asyncio.run(oqt.create_indicator(parameters, self.indicator_name))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_custom_fid_field_int(self):
        parameters = IndicatorDatabase(
            topic=self.topic_key,
            dataset=self.dataset,
            feature_id=self.feature_id,
            fid_field=self.fid_field,
        )
        indicator = asyncio.run(oqt.create_indicator(parameters, self.indicator_name))
        self.run_tests(indicator)

    @oqt_vcr.use_cassette()
    def test_create_indicator_dataset_custom_fid_field_str(self):
        parameters = IndicatorDatabase(
            topic=self.topic_key,
            dataset=self.dataset,
            feature_id="Heidelberg",
            fid_field="name",
        )
        indicator = asyncio.run(oqt.create_indicator(parameters, self.indicator_name))
        self.run_tests(indicator)

    def test_create_indicator_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            asyncio.run(oqt.create_indicator(""))

    @oqt_vcr.use_cassette()
    def test_create_report_bpolys(self):
        """Test creating report from scratch using the 'bpolys'parameters ."""
        parameters = ReportBpolys(bpolys=self.feature)
        report = asyncio.run(oqt.create_report(parameters, key=self.report_name))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.class_)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_default_fid_field(self):
        parameters = ReportDatabase(dataset=self.dataset, feature_id=self.feature_id)
        report = asyncio.run(oqt.create_report(parameters, key=self.report_name))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.class_)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_int(self):
        parameters = ReportDatabase(
            dataset=self.dataset,
            feature_id=self.feature_id,
            fid_field=self.fid_field,
        )
        report = asyncio.run(oqt.create_report(parameters, key=self.report_name))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.class_)
        self.assertIsNotNone(report.result.description)

    @oqt_vcr.use_cassette()
    def test_create_report_dataset_custom_fid_field_str(self):
        parameters = ReportDatabase(
            dataset=self.dataset,
            feature_id="Heidelberg",
            fid_field="name",
        )
        report = asyncio.run(oqt.create_report(parameters, self.report_name))
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.class_)
        self.assertIsNotNone(report.result.description)

    def test_create_report_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            asyncio.run(oqt.create_report(""))

    @oqt_vcr.use_cassette()
    def test_create_all_indicators(self):
        with mock.patch(
            "ohsome_quality_analyst.geodatabase.client.get_feature_ids",
            new_callable=AsyncMock,
        ) as get_feature_ids_mock:
            # Trigger concurrent calculation of more then 4 indicators.
            # The default semaphore is 4. Make sure no error is raised due to
            # initialization of semaphore outside the event-loop.
            get_feature_ids_mock.return_value = ["3", "12", "3", "12", "3", "12"]
            asyncio.run(
                oqt.create_all_indicators(
                    dataset="regions",
                    indicator_name="minimal",
                    topic_key="minimal",
                )
            )

    def test_check_area_size(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "europe.geojson"
        )
        with open(path, "r") as f:
            feature = geojson.load(f)
        with self.assertRaises(ValueError):
            asyncio.run(oqt.check_area_size(feature.geometry))

    def test_create_indicator_as_geojson_size_limit_bpolys(self):
        feature = get_geojson_fixture("europe.geojson")
        parameters = IndicatorBpolys(
            topic=self.topic_key,
            bpolys=feature,
        )
        with self.assertRaises(ValueError):
            asyncio.run(
                oqt.create_indicator_as_geojson(
                    parameters, key=self.indicator_name, size_restriction=True
                )
            )

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_size_limit_bpolys_ms(self):
        """Size limit is disabled for the Mapping Saturation indicator.

        Test that no error gets raised
        """
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            feature = geojson.load(f)
        parameters = IndicatorBpolys(
            topic="building_count",
            bpolys=feature,
        )
        asyncio.run(
            oqt.create_indicator_as_geojson(
                parameters, key="mapping-saturation", size_restriction=True
            )
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_size_limit_topic_data(self):
        """No error should be raised."""
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "europe.geojson"
        )
        with open(path, "r") as f:
            feature = geojson.load(f)
        parameters = IndicatorData(
            bpolys=feature,
            topic={
                "key": "key",
                "name": "name",
                "description": "description",
                "data": {
                    "result": [
                        {
                            "value": 1.0,
                            "timestamp": "2020-03-20T01:30:08.180856",
                        }
                    ]
                },
            },
        )
        asyncio.run(
            oqt.create_indicator_as_geojson(
                parameters, key="mapping-saturation", size_restriction=True
            )
        )


if __name__ == "__main__":
    unittest.main()
