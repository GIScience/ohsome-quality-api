import asyncio
from datetime import datetime

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.building_comparison.indicator import (
    BuildingComparison,
)
from tests.integrationtests.utils import oqapi_vcr


class TestInit:
    @oqapi_vcr.use_cassette
    def test_init(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        assert indicator.th_high == 0.8
        assert indicator.th_low == 0.2


class TestPreprocess:
    # @oqapi_vcr.use_cassette
    def test_preprocess(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())

        assert indicator.area_osm is not None
        assert indicator.area_osm > 0
        assert indicator.area_reference is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculate:
    @oqapi_vcr.use_cassette
    def test_calculate(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ == 5

    # @oqapi_vcr.use_cassette
    # @pytest.skip(reason="Until check_corner_cases is implemented")
    # def test_calculate_reference_area_0(
    #     self,
    #     topic_building_area,
    #     feature_germany_heidelberg,
    # ):
    #     indicator=BuildingComparison(topic_building_area, feature_germany_heidelberg)
    #     asyncio.run(indicator.preprocess())
    #     indicator.area_reference = 0
    #     indicator.calculate()
    #     assert indicator.result.value is not None
    #     assert indicator.result.value > 0


class TestFigure:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        return indicator

    # @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
