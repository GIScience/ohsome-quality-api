import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorData,
    ReportBpolys,
)
from tests.conftest import FIXTURE_DIR
from tests.integrationtests.utils import get_geojson_fixture

from .utils import oqt_vcr


class TestOqt(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.indicator_name = "minimal"
        self.report_name = "minimal"
        self.topic_key = "minimal"

        path = os.path.join(
            FIXTURE_DIR,
            "feature-collection-germany-heidelberg.geojson",
        )
        with open(path, "r") as f:
            self.feature = geojson.load(f)

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

    def test_create_report_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            asyncio.run(oqt.create_report(""))

    def test_create_indicator_as_geojson_size_limit_bpolys(self):
        feature = get_geojson_fixture("europe.geojson")  # TODO: use pytest fixture
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
            topic="building-count",
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
            # TODO: use pytest fixture
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "europe.geojson",
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
