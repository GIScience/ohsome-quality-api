import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.building_comparison.indicator import (
    BuildingComparison,
)
from tests.integrationtests.utils import oqapi_vcr


@pytest.fixture(scope="class")
def mock_get_building_area(class_mocker):
    async_mock = AsyncMock(return_value=[{"area": 4842587.791645115 / (1000 * 1000)}])
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_completeness.indicator.db_client.get_building_area",
        side_effect=async_mock,
    )


@pytest.fixture(scope="class")
def mock_get_building_area_empty(class_mocker):
    async_mock = AsyncMock(return_value=[])
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_completeness.indicator.db_client.get_building_area",
        side_effect=async_mock,
    )


class TestInit:
    @oqapi_vcr.use_cassette
    def test_init(self, topic_building_area, feature_germany_berlin):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        assert indicator.th_high == 0.85
        assert indicator.th_low == 0.5


class TestPreprocess:
    @oqapi_vcr.use_cassette
    def test_preprocess(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())

        assert indicator.area_osm is not None
        assert indicator.area_osm > 0
        assert indicator.area_references == {
            "EUBUCCO": 4.842587791645116 / (1000 * 1000)
        }
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculate:
    @oqapi_vcr.use_cassette
    def test_calculate(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ == 5

    @oqapi_vcr.use_cassette
    def test_calculate_reference_area_0(
        self,
        mock_get_building_area_empty,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.coverage["EUBUCCO"] is None
        indicator.calculate()
        assert indicator.result.value is None


class TestFigure:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        return indicator

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure

    @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)
