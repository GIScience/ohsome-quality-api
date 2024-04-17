import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.road_comparison.indicator import RoadComparison
from tests.integrationtests.utils import oqapi_vcr


@pytest.fixture
def mock_get_matched_roadlengths(class_mocker):
    async def side_effect_function(*args, **kwargs):
        if args[1] == "oqapi.microsoft_roads_europe_2022_06_08":
            return 364284, 368139
        else:
            return 25, 25

    async_mock = AsyncMock(side_effect=side_effect_function)
    class_mocker.patch(
        "ohsome_quality_api.indicators.road_comparison.indicator."
        "get_matched_roadlengths",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_matched_roadlengths_empty(class_mocker):
    async_mock = AsyncMock(return_value=(None, None))
    class_mocker.patch(
        "ohsome_quality_api.indicators.road_comparison.indicator."
        "get_matched_roadlengths",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_geom(class_mocker, feature_malta):
    async_mock = AsyncMock(return_value=feature_malta)
    class_mocker.patch(
        "ohsome_quality_api.indicators.road_comparison.indicator."
        "db_client.get_intersection_geom",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_area(class_mocker):
    async_mock = AsyncMock(return_value=1.0)
    class_mocker.patch(
        "ohsome_quality_api.indicators.road_comparison.indicator."
        "db_client.get_intersection_area",
        side_effect=async_mock,
    )


@pytest.fixture
def mock_get_intersection_area_none(class_mocker):
    async_mock = AsyncMock(return_value=0)
    class_mocker.patch(
        "ohsome_quality_api.indicators.road_comparison.indicator."
        "db_client.get_intersection_area",
        side_effect=async_mock,
    )


class TestInit:
    @oqapi_vcr.use_cassette
    def test_init(self, topic_major_roads_length, feature_malta):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        assert indicator.th_high == 0.85
        assert indicator.th_low == 0.5
        assert isinstance(indicator.data_ref, dict)

    def test_get_sources(self, topic_major_roads_length, feature_malta):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        source = indicator.format_sources()
        assert (
            "<a href='https://github.com/microsoft/RoadDetections'>"
            "Microsoft Roads</a>"
        ) in source

    def test_attribution(self, topic_major_roads_length, feature_malta):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        assert indicator.attribution is not None
        assert indicator.attribution != ""


class TestPreprocess:
    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_matched_roadlengths",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    def test_preprocess(self, topic_major_roads_length, feature_malta):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())

        for length in indicator.length_osm.values():
            assert length is not None
            assert length > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)
        for length in indicator.length_total.values():
            assert length is not None
            assert length > 0

    @oqapi_vcr.use_cassette
    def test_preprocess_no_intersection(
        self,
        topic_major_roads_length,
        feature_malta,
        mock_get_intersection_area_none,
    ):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())

        for area in indicator.area_cov.values():
            assert area == 0.0
        assert isinstance(indicator.result.timestamp, datetime)
        assert indicator.result.timestamp_osm is None


class TestCalculate:
    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_matched_roadlengths",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    def test_calculate(
        self,
        topic_major_roads_length,
        feature_malta,
    ):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value > 0
        assert indicator.result.class_ is not None
        assert indicator.result.class_ >= 0

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_matched_roadlengths_empty",
        "mock_get_intersection_area",
        "mock_get_intersection_geom",
    )
    def test_calculate_reference_lenght_0(
        self,
        topic_major_roads_length,
        feature_malta,
    ):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.result.value is None
        assert indicator.result.class_ is None
        assert indicator.result.label == "undefined"
        assert (
            ", but has no road length. No quality estimation with reference is "
            "possible." in indicator.result.description
        )

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures("mock_get_intersection_area_none")
    def test_calculate_no_intersection(
        self,
        topic_major_roads_length,
        feature_malta,
    ):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
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


class TestFigure:
    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_matched_roadlengths",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    def test_create_figure(self, topic_major_roads_length, feature_malta):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure

    @oqapi_vcr.use_cassette
    @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    @pytest.mark.usefixtures(
        "mock_get_matched_roadlengths",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    def test_create_figure_manual(self, topic_major_roads_length, feature_malta):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        pio.show(indicator.result.figure)

    @oqapi_vcr.use_cassette
    @pytest.mark.usefixtures(
        "mock_get_matched_roadlengths_empty",
        "mock_get_intersection_geom",
        "mock_get_intersection_area",
    )
    def test_create_figure_building_area_zero(
        self, topic_major_roads_length, feature_malta
    ):
        indicator = RoadComparison(topic_major_roads_length, feature_malta)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)
