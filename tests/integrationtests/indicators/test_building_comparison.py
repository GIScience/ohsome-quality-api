import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.building_comparison.indicator import (
    BuildingComparison,
    get_sources,
    load_datasets_coverage_names,
    load_reference_datasets,
)
from tests.integrationtests.utils import oqapi_vcr


@pytest.fixture
def mock_get_building_area(class_mocker):
    async def side_effect_function(*args, **kwargs):
        if args[1] == "EUBUCCO":
            return 6000000.791645115
        else:
            return 5000000.791645115

    async_mock = AsyncMock(side_effect=side_effect_function)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_reference_building_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_building_area_low(class_mocker):
    async_mock = AsyncMock(return_value=1)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_reference_building_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_building_area_low_and_expected(class_mocker):
    async def side_effect_function(*args, **kwargs):
        if args[1] == "EUBUCCO":
            return 1
        else:
            return 6000000.791645115

    async_mock = AsyncMock(side_effect=side_effect_function)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_reference_building_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_building_area_empty(class_mocker):
    async_mock = AsyncMock(return_value=0)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_reference_building_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_geom(class_mocker, feature_germany_berlin):
    async_mock = AsyncMock(return_value=feature_germany_berlin)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_intersection_geom",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_area(class_mocker):
    async_mock = AsyncMock(return_value=1.0)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_intersection_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_area_none(class_mocker):
    async_mock = AsyncMock(return_value=0)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_intersection_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_area_some(class_mocker):
    async def side_effect(*args, **kwargs):
        if "eubucco" in args[1]:
            return 0.0
        else:
            return 1.0

    async_mock = AsyncMock(side_effect=side_effect)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_intersection_area",
        side_effect=async_mock,
    )


class TestInit:
    @oqapi_vcr.use_cassette
    def test_init(self, topic_building_area, feature_germany_berlin):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        assert indicator.th_high == 0.85
        assert indicator.th_low == 0.5
        assert isinstance(indicator.data_ref, dict)


class TestPreprocess:
    @oqapi_vcr.use_cassette
    def test_preprocess(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
        mock_get_intersection_area,
        mock_get_intersection_geom,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())

        for area in indicator.area_osm.values():
            assert area is not None
            assert area > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette
    def test_preprocess_no_intersection(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
        mock_get_intersection_area_none,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())

        for area in indicator.area_cov.values():
            assert area == 0.0
        assert isinstance(indicator.result.timestamp, datetime)
        assert indicator.result.timestamp_osm is None

    # TODO
    @oqapi_vcr.use_cassette
    @pytest.mark.skip()
    def test_preprocess_some_intersection(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
        mock_get_intersection_area_some,
        mock_get_intersection_geom,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())

        assert 1.0 in list(indicator.area_cov.values())
        assert 0.0 in list(indicator.area_cov.values())
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculate:
    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    def test_calculate(
        self,
        topic_building_area,
        feature_germany_berlin,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area_empty",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    def test_calculate_reference_area_0(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value == 0.0

    @oqapi_vcr.use_cassette
    def test_calculate_above_one_th(
        self,
        mock_get_building_area_low,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_reference_coverage_intersection_area,
        mock_get_reference_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        assert indicator.result.description is not None
        assert (
            "Warning: Because of a big difference between OSM and the"
            " reference in all reference data. No quality estimation"
            " will be calculated. " in indicator.result.description
        )
        assert indicator.result.label == "undefined"

    @oqapi_vcr.use_cassette
    def test_calculate_no_intersection(
        self,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_reference_coverage_intersection_area_no_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        assert indicator.result.description is not None
        assert (
            "Comparison could not be made. None of the reference datasets covers the "
            "area-of-interest." in indicator.result.description
        )
        assert indicator.result.label == "undefined"

    @oqapi_vcr.use_cassette
    def test_calculate_some_intersection(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_reference_coverage_intersection_area_some_intersection,
        mock_get_reference_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0
        assert indicator.result.description is not None
        assert (
            "Reference dataset EUBUCCO does not cover area-of-interest."
            in indicator.result.description
        )
        assert (
            "of the area-of-interest is covered by the reference dataset"
            in indicator.result.description
        )

    @oqapi_vcr.use_cassette
    def test_calculate_above_one_th_and_expected(
        self,
        mock_get_building_area_low_and_expected,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_reference_coverage_intersection_area,
        mock_get_reference_coverage_intersection,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0
        assert indicator.result.label != "undefined"
        assert indicator.result.description is not None
        assert (
            "of the area-of-interest is covered by the reference dataset"
            in indicator.result.description
        )
        assert (
            "this data is not considered in the overall result value."
            in indicator.result.description
        )


class TestFigure:
    @pytest.fixture
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_berlin,
        mock_get_reference_coverage_intersection_area,
        mock_get_reference_coverage_intersection,
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

    @oqapi_vcr.use_cassette
    def test_create_figure_above_one_th(
        self,
        mock_get_building_area_low,
        topic_building_area,
        feature_germany_berlin,
        mock_get_reference_coverage_intersection_area,
        mock_get_reference_coverage_intersection,
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
        mock_get_reference_coverage_intersection_area,
        mock_get_reference_coverage_intersection,
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
