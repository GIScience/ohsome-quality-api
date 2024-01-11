import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.building_comparison.indicator import (
    BuildingComparison,
    get_sources,
    load_reference_datasets,
)
from tests.integrationtests.utils import oqapi_vcr


@pytest.fixture(scope="class")
def mock_get_building_area(class_mocker):
    async_mock = AsyncMock(return_value=4842587.791645115)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_eubucco_building_area",
        side_effect=async_mock,
    )


@pytest.fixture(scope="class")
def mock_get_building_area_low(class_mocker):
    async_mock = AsyncMock(return_value=1)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_eubucco_building_area",
        side_effect=async_mock,
    )


@pytest.fixture(scope="class")
def mock_get_building_area_empty(class_mocker):
    async_mock = AsyncMock(return_value=0)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_eubucco_building_area",
        side_effect=async_mock,
    )
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_microsoft_building_area",
        side_effect=async_mock,
    )


@pytest.fixture(scope="class")
def mock_get_eubucco_coverage_intersection(class_mocker, feature_germany_berlin):
    async_mock = AsyncMock(return_value=feature_germany_berlin)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_eubucco_coverage_intersection",
        side_effect=async_mock,
    )


@pytest.fixture(scope="class")
def mock_get_eubucco_coverage_intersection_area(class_mocker):
    async_mock = AsyncMock(return_value=[{"area_ratio": 1}])
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_eubucco_coverage_intersection_area",
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
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())

        assert indicator.area_osm is not None
        assert indicator.area_osm > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculate:
    @oqapi_vcr.use_cassette
    def test_calculate(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0

    @oqapi_vcr.use_cassette
    def test_calculate_reference_area_0(
        self,
        mock_get_building_area_empty,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.coverage["EUBUCCO"] is None
        indicator.calculate()
        assert indicator.result.value is None

    @oqapi_vcr.use_cassette
    def test_calculate_above_one_th(
        self,
        mock_get_building_area_low,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is None
        assert indicator.result.description is not None
        assert (
            "Warning: Because of a big difference between OSM and the reference "
            + "data no quality estimation has been made. "
            + "It could be that the reference data is outdated. "
            in indicator.result.description
        )
        assert indicator.result.label == "undefined"


class TestFigure:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        return indicator

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure

    # @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    @oqapi_vcr.use_cassette
    def test_create_figure_above_one_th(
        self,
        mock_get_building_area_low,
        topic_building_area,
        feature_germany_berlin,
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert indicator.result.figure["data"][0]["type"] == "bar"
        pgo.Figure(indicator.result.figure)

    @oqapi_vcr.use_cassette
    def test_create_figure_building_area_zero(
        self,
        mock_get_building_area_empty,
        topic_building_area,
        feature_germany_berlin,
        mock_get_eubucco_coverage_intersection_area,
        mock_get_eubucco_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert indicator.result.figure["data"][0]["type"] == "bar"
        pgo.Figure(indicator.result.figure)


def test_get_sources():
    source = get_sources(["EUBUCCO"])
    assert source == "<a href='https://docs.eubucco.com/'>EUBUCCO</a>"


def test_load_reference_datasets():
    reference_datasets = load_reference_datasets()
    assert reference_datasets is not None
    assert isinstance(reference_datasets, list)
    assert len(reference_datasets) > 0
