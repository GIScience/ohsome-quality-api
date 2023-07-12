import asyncio

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_analyst.indicators.minimal.indicator import Minimal
from tests.integrationtests.utils import oqt_vcr


class TestAttribution:
    @oqt_vcr.use_cassette
    def test_attribution(self, topic_minimal, feature_germany_heidelberg):
        indicator = Minimal(topic_minimal, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        assert indicator.attribution() is not None


class TestPreprocess:
    @oqt_vcr.use_cassette
    def test_preprocess(self, topic_minimal, feature_germany_heidelberg):
        indicator = Minimal(topic_minimal, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        assert indicator.count is not None


class TestCalculate:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_minimal, feature_germany_heidelberg):
        i = Minimal(topic_minimal, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.result.value is not None
        assert indicator.result.label is not None
        assert indicator.result.description is not None
        assert indicator.result.timestamp_oqt is not None
        assert indicator.result.timestamp_osm is not None


class TestFigure:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_minimal, feature_germany_heidelberg):
        i = Minimal(topic_minimal, feature_germany_heidelberg)
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
