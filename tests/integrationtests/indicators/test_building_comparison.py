from datetime import datetime
from unittest.mock import AsyncMock

import asyncpg_recorder
import pytest
from pytest_approval.main import verify, verify_plotly

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.indicators.building_comparison.indicator import (
    BuildingComparison,
)
from tests.integrationtests.utils import oqapi_vcr


@pytest.fixture(autouse=True, params=[False, True])
def ohsomedb_feature_flag(request, monkeypatch):
    def get_config_value_(key: str):
        if key == "ohsomedb_enabled":
            return request.param
        else:
            return get_config_value(key)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.building_comparison.indicator.get_config_value",
        get_config_value_,
    )


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
def mock_get_intersection_geom(class_mocker, feature_germany_heidelberg):
    async_mock = AsyncMock(return_value=feature_germany_heidelberg)
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
    def test_init(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        assert indicator.th_high == 0.85
        assert indicator.th_low == 0.5
        assert isinstance(indicator.data_ref, dict)

    def test_get_sources(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        source = indicator.format_sources()
        assert "<a href='https://docs.eubucco.com/'>EUBUCCO</a>" in source

    def test_attribution(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        assert indicator.attribution is not None
        assert indicator.attribution != ""


class TestPreprocess:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        assert indicator.area_osm in [
            {
                "EUBUCCO": 6.592363,
                "Microsoft Buildings": 6.592363,
            },
            {
                "EUBUCCO": 6.58471776,
                "Microsoft Buildings": 6.58471776,
            },
        ]
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess_no_intersection(
        self,
        mock_get_building_area,
        topic_building_area,
        feature_germany_heidelberg,
        mock_get_intersection_area_none,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()

        for area in indicator.area_cov.values():
            assert area == pytest.approx(0.0)
        assert isinstance(indicator.result.timestamp, datetime)
        assert indicator.result.timestamp_osm is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area_some",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess_some_intersection(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()

        assert 1.0 in list(indicator.area_cov.values())
        assert 0.0 in list(indicator.area_cov.values())
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculate:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.ratio in [
            {"EUBUCCO": 1.3184723912475542, "Microsoft Buildings": 1.3184723912475542},
            {"EUBUCCO": 1.316943343489647, "Microsoft Buildings": 1.316943343489647},
        ]
        assert indicator.result.value in [None, 1.0104228420207384]
        assert indicator.result.class_ in [None, 5]
        assert verify(indicator.result.description)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area_empty",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_reference_area_0(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
        "mock_get_building_area_low",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_above_one_th(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        for v in indicator.area_ref.values():
            assert v is not None
        for v in indicator.area_osm.values():
            assert v is not None
        assert indicator.result.label == "undefined"
        assert verify(indicator.result.description)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("mock_get_intersection_area_none")
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_no_intersection(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        assert indicator.result.label == "undefined"
        assert verify(indicator.result.description)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area_some",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_some_intersection(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value in [None, 1.0104228420207384]
        assert indicator.result.class_ in [None, 5]
        # major edge case description
        assert verify(indicator.result.description)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
        "mock_get_building_area_low_some",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_above_one_th_and_expected(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0
        assert indicator.result.label != "undefined"
        assert verify(indicator.result.description)


class TestFigure:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_create_figure(self, topic_building_area, feature_germany_heidelberg):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert verify_plotly(indicator.result.figure)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_create_figure_above_one_th(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert indicator.result.figure["data"][0]["type"] == "bar"
        assert verify_plotly(indicator.result.figure)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures(
        "mock_get_building_area_empty",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_create_figure_building_area_zero(
        self,
        topic_building_area,
        feature_germany_heidelberg,
    ):
        indicator = BuildingComparison(topic_building_area, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert indicator.result.figure["data"][0]["type"] == "pie"
        assert verify_plotly(indicator.result.figure)
