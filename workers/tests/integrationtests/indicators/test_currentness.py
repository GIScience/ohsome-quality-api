import asyncio
import os
from datetime import datetime

import geojson
import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_analyst.indicators.currentness.indicator import (
    Currentness,
    get_last_edited_year,
    get_median_year,
)
from tests.integrationtests.utils import get_topic_fixture, oqt_vcr


class TestPreprocess:
    @oqt_vcr.use_cassette
    def test_preprocess(self, topic_building_count, feature_germany_heidelberg):
        indicator = Currentness(topic_building_count, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        assert len(indicator.contrib_abs) > 0
        assert indicator.contrib_sum > 0
        assert isinstance(indicator.result.timestamp_oqt, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = Currentness(topic_building_count, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.result.value >= 0.0
        assert indicator.result.label == "green"
        assert indicator.result.description is not None

    @oqt_vcr.use_cassette()
    def test_no_amenities(self):
        """Test area with no amenities"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = Currentness(feature=feature, topic=get_topic_fixture("amenities"))
        asyncio.run(indicator.preprocess())
        assert indicator.contrib_sum == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None
        assert indicator.result.description == (
            "In the area of interest no features of the selected topic are present "
            + "today."
        )


class TestFigure:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = Currentness(topic_building_count, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    # comment out for manual test
    @pytest.mark.skip(reason="Only for manual testing.")
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
        assert indicator.result.svg is not None


def test_get_last_edited_year():
    given = [3, 0, 5, 0]
    expected = 0
    result = get_last_edited_year(given)
    assert result == expected

    given = [0, 0, 5, 0]
    expected = 2
    result = get_last_edited_year(given)
    assert result == expected


def test_get_median_year():
    given = [0.2, 0, 0.6, 0.2]
    expected = 2
    result = get_median_year(given)
    assert result == expected

    given = [0.6, 0, 0.2, 0.2]
    expected = 0
    result = get_median_year(given)
    assert result == expected
