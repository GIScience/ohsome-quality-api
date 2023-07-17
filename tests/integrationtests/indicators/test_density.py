import asyncio
from datetime import datetime

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_analyst.indicators.density.indicator import Density
from ohsome_quality_analyst.topics.definitions import get_topic_definition
from ohsome_quality_analyst.topics.models import TopicDefinition
from tests.integrationtests.utils import oqt_vcr


@pytest.fixture(scope="class")
def topic_poi() -> TopicDefinition:
    return get_topic_definition("poi")


class TestPreprocess:
    @oqt_vcr.use_cassette
    def test_preprocess(self, topic_poi, feature_germany_heidelberg):
        indicator = Density(topic_poi, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        assert indicator.area_sqkm is not None
        assert indicator.count is not None
        assert isinstance(indicator.result.timestamp_oqt, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_poi, feature_germany_heidelberg):
        i = Density(topic_poi, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.result.value is not None
        assert indicator.result.label is not None
        assert indicator.result.description is not None


class TestFigure:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_poi, feature_germany_heidelberg):
        i = Density(topic_poi, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        i.create_figure()
        return i

    # comment out for manual test
    @pytest.mark.skip(reason="Only for manual testing.")
    def test_create_figure_manual(self, indicator):
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
        assert indicator.result.svg is not None
