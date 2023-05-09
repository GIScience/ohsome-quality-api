import asyncio
import os
from datetime import datetime

import geojson
import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_analyst.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)
from tests.integrationtests.utils import get_topic_fixture, oqt_vcr


class TestPreprocess:
    @oqt_vcr.use_cassette
    def test_preprocess(self, topic_building_count, feature_germany_heidelberg):
        indicator = AttributeCompleteness(
            topic_building_count, feature_germany_heidelberg
        )
        asyncio.run(indicator.preprocess())
        assert isinstance(indicator.result.timestamp_oqt, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = AttributeCompleteness(topic_building_count, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.result.value >= 0.0
        assert indicator.result.label in ["green", "yellow", "red", "undefined"]
        assert indicator.result.description is not None

        assert isinstance(indicator.result.timestamp_osm, datetime)
        assert isinstance(indicator.result.timestamp_oqt, datetime)

    @oqt_vcr.use_cassette()
    def test_no_features(self):
        """Test area with no features"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = AttributeCompleteness(
            topic=get_topic_fixture("clc_leaf_type"),
            feature=feature,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.count_all == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None


class TestFigure:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = AttributeCompleteness(topic_building_count, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
        assert indicator.result.svg is not None
