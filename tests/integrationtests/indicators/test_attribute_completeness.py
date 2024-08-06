import asyncio
import os
from datetime import datetime

import geojson
import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)
from tests.integrationtests.utils import get_topic_fixture, oqapi_vcr


class TestPreprocess:
    @oqapi_vcr.use_cassette
    def test_preprocess(
        self, topic_building_count, feature_germany_heidelberg, attribute_key
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette
    def test_preprocess_multiple_attribute_keys(
        self, topic_building_count, feature_germany_heidelberg, attribute_key_multiple
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key_multiple,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_key,
    ):
        i = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key,
        )
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.result.value is not None
        assert indicator.result.value >= 0.0
        assert indicator.result.label != "red"
        assert indicator.result.description is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette()
    def test_no_features(self, attribute):
        """Test area with no features"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = AttributeCompleteness(
            topic=get_topic_fixture("clc-leaf-type"),
            feature=feature,
            attribute_key=["leaf_type"],
        )
        asyncio.run(indicator.preprocess())
        assert indicator.absolute_value_1 == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None


class TestFigure:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_key,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key,
        )
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        return indicator

    # comment out for manual test
    @pytest.mark.skip(reason="Only for manual testing.")
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
