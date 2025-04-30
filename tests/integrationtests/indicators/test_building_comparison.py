import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from approvaltests import Options, verify, verify_as_json
from pydantic_core import to_jsonable_python

from ohsome_quality_api.indicators.building_comparison.indicator import (
    BuildingComparison,
)
from tests.approvaltests_namers import PytestNamer
from tests.approvaltests_reporters import PlotlyDiffReporter
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
    async_mock = AsyncMock(return_value=1000000)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_reference_building_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_building_area_low_some(class_mocker):
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
            return 0.0  # 0 %
        else:
            return 1.0  # 100 %

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

    def test_get_sources(self, topic_building_area, feature_germany_berlin):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        source = indicator.format_sources()
        assert "<a href='https://docs.eubucco.com/'>EUBUCCO</a>" in source

    def test_attribution(self, topic_building_area, feature_germany_berlin):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        assert indicator.attribution is not None
        assert indicator.attribution != ""


class TestPreprocess:
    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    def test_preprocess(self, topic_building_area, feature_germany_berlin):
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
            assert area == pytest.approx(0.0)
        assert isinstance(indicator.result.timestamp, datetime)
        assert indicator.result.timestamp_osm is None

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area_some",
    )
    def test_preprocess_some_intersection(
        self,
        topic_building_area,
        feature_germany_berlin,
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
        verify(indicator.result.description, namer=PytestNamer())

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
        assert indicator.result.value is None

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
        "mock_get_building_area_low",
    )
    def test_calculate_above_one_th(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        for v in indicator.area_ref.values():
            assert v is not None
        for v in indicator.area_osm.values():
            assert v is not None
        assert indicator.result.label == "undefined"
        verify(indicator.result.description, namer=PytestNamer())

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures("mock_get_intersection_area_none")
    def test_calculate_no_intersection(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        assert indicator.result.label == "undefined"
        verify(indicator.result.description, namer=PytestNamer())

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area_some",
    )
    def test_calculate_some_intersection(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0
        # major edge case description
        verify(indicator.result.description, namer=PytestNamer())

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
        "mock_get_building_area_low_some",
    )
    def test_calculate_above_one_th_and_expected(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0
        assert indicator.result.label != "undefined"
        verify(indicator.result.description, namer=PytestNamer())


class TestFigure:
    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    def test_create_figure(self, topic_building_area, feature_germany_berlin):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        verify_as_json(
            to_jsonable_python(indicator.result.figure),
            options=Options()
            .with_reporter(PlotlyDiffReporter())
            .with_namer(PytestNamer()),
        )

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    def test_create_figure_above_one_th(
        self,
        topic_building_area,
        feature_germany_berlin,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert indicator.result.figure["data"][0]["type"] == "bar"
        verify_as_json(
            to_jsonable_python(indicator.result.figure),
            options=Options()
            .with_reporter(PlotlyDiffReporter())
            .with_namer(PytestNamer()),
        )

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_building_area_empty",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    def test_create_figure_building_area_zero(
        self,
        topic_building_area,
        feature_germany_berlin,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_berlin)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert indicator.result.figure["data"][0]["type"] == "pie"
        verify_as_json(
            to_jsonable_python(indicator.result.figure),
            options=Options()
            .with_reporter(PlotlyDiffReporter())
            .with_namer(PytestNamer()),
        )
