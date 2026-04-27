import os
from datetime import datetime

import asyncpg_recorder
import geojson
import pytest
from pytest_approval.main import verify, verify_plotly

from ohsome_quality_api.attributes.definitions import get_attributes
from ohsome_quality_api.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)
from tests.integrationtests.utils import (
    get_topic_fixture,
    oqapi_vcr,
)


@pytest.fixture(autouse=True, params=[True, False])
def ohsomedb_feature_flag(request, monkeypatch):
    monkeypatch.setattr(
        "ohsome_quality_api.indicators.attribute_completeness.indicator.is_ohsomedb_enabled",
        lambda: request.param,
    )


class TestPreprocess:
    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess_attribute_keys_single(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_key,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_keys=attribute_key,
        )
        await indicator.preprocess()
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess_attribute_keys_multiple(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_key_multiple,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_keys=attribute_key_multiple,
        )
        await indicator.preprocess()
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess_attribute_filter(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_filter,
        attribute_title,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_filter=attribute_filter,
            attribute_title=attribute_title,
        )
        await indicator.preprocess()
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_with_attribute_keys(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_keys=["height"],
        )
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value >= 0.0
        assert indicator.result.label != "red"
        assert indicator.result.description is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)
        assert verify(indicator.result.description)

    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_with_attribute_filter(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_filter="height=* or building:levels=*",
            attribute_title="Heigit",
        )
        await indicator.preprocess()
        indicator.calculate()
        assert indicator.result.value is not None
        assert indicator.result.value >= 0.0
        assert indicator.result.label != "red"
        assert indicator.result.description is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)
        assert verify(indicator.result.description)

    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_no_features(self):
        """Test area with no features"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = AttributeCompleteness(
            topic=get_topic_fixture("clc-leaf-type"),
            feature=feature,
            attribute_keys=["leaf-type"],
        )
        await indicator.preprocess()
        assert indicator.absolute_value_1 == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None


class TestFigure:
    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_create_figure_with_attribute_keys(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            ["height"],
        )
        await indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert verify_plotly(indicator.result.figure)

    @pytest.mark.asyncio
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_create_figure_with_attribute_filter(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_filter="height=* or building:levels=*",
            attribute_title="Height",
        )
        await indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        assert verify_plotly(indicator.result.figure)


def test_create_description_attribute_keys_single(feature_germany_heidelberg):
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        feature_germany_heidelberg,
        ["height"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    assert indicator.description is not None
    assert verify(indicator.description)


def test_create_description_attribute_keys_multiple(feature_germany_heidelberg):
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        feature_germany_heidelberg,
        ["height", "house-number", "address-street"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    assert indicator.description is not None
    assert verify(indicator.description)


def test_create_description_attribute_filter(
    attribute_filter,
    attribute_title,
    feature_germany_heidelberg,
):
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        feature_germany_heidelberg,
        attribute_filter=attribute_filter,
        attribute_title=attribute_title,
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    assert indicator.description is not None
    assert verify(indicator.description)


@pytest.mark.parametrize(
    "topic_key, attribute_key, aggregation, "
    "result_value, absolute_value_1, absolute_value_2",
    [
        ("building-count", "height", "elements", 0.2, 10, 2),
        ("clc-leaf-type", "leaf-type", "m²", 0.2, 10.012, 2.012),
        ("roads", "name", "m", 0.2, 10.012, 2.012),
    ],
)
def test_create_description_multiple_aggregation_types(
    topic_key,
    attribute_key,
    aggregation,
    result_value,
    absolute_value_1,
    absolute_value_2,
    feature_germany_heidelberg,
):
    indicator = AttributeCompleteness(
        get_topic_fixture(topic_key),
        feature_germany_heidelberg,
        [attribute_key],
    )
    indicator.result.value = result_value
    indicator.absolute_value_1 = absolute_value_1
    indicator.absolute_value_2 = absolute_value_2
    indicator.create_description()
    assert indicator.description is not None
    assert aggregation in indicator.description


def test_filters_match(
    topic_key_building_count,
    feature_germany_heidelberg,
    attribute_key_height,
):
    indicator_attribute_keys = AttributeCompleteness(
        get_topic_fixture(topic_key_building_count),
        feature_germany_heidelberg,
        attribute_keys=attribute_key_height,
    )

    attributes = get_attributes()

    attribute_filter = attributes[topic_key_building_count][
        attribute_key_height[0]
    ].filter
    indicator_attribute_filter = AttributeCompleteness(
        get_topic_fixture(topic_key_building_count),
        feature_germany_heidelberg,
        attribute_filter=attribute_filter,
        attribute_title="foo",
    )
    assert (
        indicator_attribute_filter.attribute_filter
        == indicator_attribute_keys.attribute_filter
    )
