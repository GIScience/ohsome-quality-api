import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

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


# @pytest.fixture
# def mock_get_building_area_low(class_mocker):
#     async_mock = AsyncMock(return_value=1000000)
#     class_mocker.patch(
#         "ohsome_quality_api.indicators.road_comparison.indicator.
#         get_matched_roadlengths",
#         side_effect=async_mock,
#     )


# @pytest.fixture
# def mock_get_building_area_low_some(class_mocker):
#     async def side_effect_function(*args, **kwargs):
#         if args[1] == "EUBUCCO":
#             return 1
#         else:
#             return 6000000.791645115
#
#     async_mock = AsyncMock(side_effect=side_effect_function)
#     class_mocker.patch(
#         "ohsome_quality_api.indicators.road_comparison.indicator.
#         get_reference_building_area",
#         side_effect=async_mock,
#     )
#
#
# @pytest.fixture
# def mock_get_building_area_empty(class_mocker):
#     async_mock = AsyncMock(return_value=0)
#     class_mocker.patch(
#         "ohsome_quality_api.indicators.road_comparison.indicator.
#         get_reference_building_area",
#         side_effect=async_mock,
#     )


# @pytest.fixture
# def mock_get_intersection_area_some(class_mocker):
#     async def side_effect(*args, **kwargs):
#         if "eubucco" in args[1]:
#             return 0.0  # 0 %
#         else:
#             return 1.0  # 100 %
#
#     async_mock = AsyncMock(side_effect=side_effect)
#     class_mocker.patch(
#         "ohsome_quality_api.indicators.road_comparison.indicator.
#         db_client.get_intersection_area",
#         side_effect=async_mock,
#     )


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


#     @oqapi_vcr.use_cassette
#     def test_preprocess_no_intersection(
#         self,
#         mock_get_matched_roadlengths,
#         topic_building_area,
#         feature_germany_berlin,
#         mock_get_intersection_area_none,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_berlin)
#         asyncio.run(indicator.preprocess())
#
#         for area in indicator.area_cov.values():
#             assert area == 0.0
#         assert isinstance(indicator.result.timestamp, datetime)
#         assert indicator.result.timestamp_osm is None
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_building_area_low",
#         "mock_get_intersection_geom",
#         "mock_get_intersection_area_some",
#     )
#     def test_preprocess_some_intersection(
#         self,
#         topic_building_area,
#         feature_germany_berlin,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_berlin)
#         asyncio.run(indicator.preprocess())
#
#         assert 1.0 in list(indicator.area_cov.values())
#         assert isinstance(indicator.result.timestamp, datetime)
#         assert isinstance(indicator.result.timestamp_osm, datetime)
#
#
# class TestCalculate:
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_intersection_area",
#         "mock_get_intersection_geom",
#     )
#     def test_calculate(
#         self,
#         topic_major_roads_length,
#         feature_malta,
#     ):
#         indicator = RoadComparison(topic_major_roads_length, feature_malta)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         assert indicator.result.value is not None
#         assert indicator.result.value > 0
#         assert indicator.result.class_ is not None
#         assert indicator.result.class_ >= 0
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_building_area_empty",
#         "mock_get_intersection_area",
#         "mock_get_intersection_geom",
#     )
#     def test_calculate_reference_area_0(
#         self,
#         topic_building_area,
#         feature_germany_heidelberg,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_heidelberg)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         assert indicator.result.value is None
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_intersection_area",
#         "mock_get_intersection_geom",
#         "mock_get_building_area_low",
#     )
#     def test_calculate_above_one_th(
#         self,
#         topic_building_area,
#         feature_germany_heidelberg,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_heidelberg)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         assert indicator.result.value is None
#         assert indicator.result.class_ is None
#         assert indicator.result.description is not None
#         for v in indicator.area_ref.values():
#             assert v is not None
#         for v in indicator.area_osm.values():
#             assert v is not None
#         assert (
#             "Warning: OSM has substantivly more buildings mapped than the Reference "
#             "datasets. No quality estimation has been made."
#             in indicator.result.description
#         )
#         assert indicator.result.label == "undefined"
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures()
#     def test_calculate_no_intersection(
#         self,
#         topic_building_area,
#         feature_germany_heidelberg,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_heidelberg)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         assert indicator.result.value is None
#         assert indicator.result.class_ is None
#         assert indicator.result.description is not None
#         assert (
#             "Comparison could not be made. None of the reference datasets covers the "
#             "area-of-interest." in indicator.result.description
#         )
#         assert indicator.result.label == "undefined"
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures()
#     def test_calculate_some_intersection(
#         self,
#         topic_building_area,
#         feature_germany_heidelberg,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_heidelberg)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         assert indicator.result.value is not None
#         assert indicator.result.value > 0
#         assert indicator.result.class_ is not None
#         assert indicator.result.class_ >= 0
#         assert indicator.result.description is not None
#         # major edge case description
#         assert (
#             "Reference dataset EUBUCCO does not cover area-of-interest."
#             in indicator.result.description
#         )
#         assert (
#             "of the area-of-interest is covered by the reference dataset"
#             in indicator.result.description
#         )
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_building_area",
#         "mock_get_intersection_geom",
#         "mock_get_intersection_area",
#         "mock_get_building_area_low_some",
#     )
#     def test_calculate_above_one_th_and_expected(
#         self,
#         topic_building_area,
#         feature_germany_heidelberg,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_heidelberg)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         assert indicator.result.value is not None
#         assert indicator.result.value > 0
#         assert indicator.result.class_ is not None
#         assert indicator.result.class_ >= 0
#         assert indicator.result.label != "undefined"
#         assert indicator.result.description is not None
#         assert (
#             "of the area-of-interest is covered by the reference dataset"
#             in indicator.result.description
#         )
#         # TODO: should user be warned if a dataset was not fit for comparison?
#         # -> for ratio above self.above_one_th
#         # assert (
#         #     "this data is not considered in the overall result value."
#         #     in indicator.result.description
#         # )
#
#
# class TestFigure:
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_building_area",
#         "mock_get_intersection_geom",
#         "mock_get_intersection_area",
#     )
#     def test_create_figure(self, topic_building_area, feature_germany_berlin):
#         indicator = RoadComparison(topic_building_area, feature_germany_berlin)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         indicator.create_figure()
#         assert isinstance(indicator.result.figure, dict)
#         pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
#     @pytest.mark.usefixtures(
#         "mock_get_building_area",
#         "mock_get_intersection_geom",
#         "mock_get_intersection_area",
#     )
#     def test_create_figure_manual(self, topic_building_area, feature_germany_berlin):
#         indicator = RoadComparison(topic_building_area, feature_germany_berlin)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         indicator.create_figure()
#         pio.show(indicator.result.figure)
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_building_area",
#         "mock_get_intersection_geom",
#         "mock_get_intersection_area",
#     )
#     def test_create_figure_above_one_th(
#         self,
#         topic_building_area,
#         feature_germany_berlin,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_berlin)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         indicator.create_figure()
#         assert isinstance(indicator.result.figure, dict)
#         assert indicator.result.figure["data"][0]["type"] == "bar"
#         pgo.Figure(indicator.result.figure)
#
#     @oqapi_vcr.use_cassette
#     @pytest.mark.usefixtures(
#         "mock_get_building_area",
#         "mock_get_intersection_geom",
#         "mock_get_intersection_area",
#     )
#     def test_create_figure_building_area_zero(
#         self,
#         topic_building_area,
#         feature_germany_berlin,
#     ):
#         indicator = RoadComparison(topic_building_area, feature_germany_berlin)
#         asyncio.run(indicator.preprocess())
#         indicator.calculate()
#         indicator.create_figure()
#         assert isinstance(indicator.result.figure, dict)
#         assert indicator.result.figure["data"][0]["type"] == "bar"
#         pgo.Figure(indicator.result.figure)
