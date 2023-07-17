import asyncio
import os
import unittest
from unittest import mock

import geojson
import pytest

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import (
    IndicatorDataRequest,
    IndicatorRequest,
)
from tests.conftest import FIXTURE_DIR
from tests.integrationtests.utils import oqt_vcr


@oqt_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "topic_minimal"),
        ("mapping-saturation", "topic_building_count"),
        ("currentness", "topic_building_count"),
        ("attribute-completeness", "topic_building_count"),
    ],
)
def test_create_indicator(feature, indicator, topic, request):
    """Minimal viable request for a single bpoly."""
    topic = request.getfixturevalue(topic)
    indicator = asyncio.run(oqt._create_indicator(indicator, feature, topic))
    assert indicator.result.label is not None
    assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.result.figure is not None


@oqt_vcr.use_cassette
def test_create_report(feature):
    report = asyncio.run(oqt._create_report("minimal", feature))
    assert report.result.label is not None
    assert report.result.class_ is not None
    assert report.result.description is not None


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

    @mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
    def test_create_indicator_as_geojson_size_limit_bpolys(self):
        parameters = IndicatorRequest(
            topic=self.topic_key,
            bpolys=self.feature,
        )
        with self.assertRaises(ValueError):
            asyncio.run(oqt.create_indicator(parameters, key=self.indicator_name))

    @mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
    @oqt_vcr.use_cassette
    def test_create_indicator_as_geojson_size_limit_bpolys_ms(self):
        """Size limit is disabled for the Mapping Saturation indicator.

        Test that no error gets raised.
        """
        parameters = IndicatorRequest(
            topic="building-count",
            bpolys=self.feature,
        )
        asyncio.run(oqt.create_indicator(parameters, key="mapping-saturation"))

    @mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
    @oqt_vcr.use_cassette
    def test_create_indicator_as_geojson_size_limit_topic_data(self):
        """Size limit is disabled for request with custom data.

        Test that no error gets raised.
        """
        parameters = IndicatorDataRequest(
            bpolys=self.feature,
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
        asyncio.run(oqt.create_indicator(parameters, key="mapping-saturation"))


if __name__ == "__main__":
    unittest.main()
