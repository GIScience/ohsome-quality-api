import asyncio

import asyncpg_recorder
import pytest

from ohsome_quality_api import main
from tests.integrationtests.utils import oqapi_vcr

# TODO: add user-activity and land-cover-... indicators (ohsomedb)
PARAMETERS = [
    ("mapping-saturation", "topic_building_count", {}),
    ("mapping-saturation", "topic_custom", {}),
    ("currentness", "topic_building_count", {}),
    ("currentness", "topic_custom", {}),
    (
        "attribute-completeness",
        "topic_building_count",
        {"attribute_keys": ["height"]},
    ),
    (
        "attribute-completeness",
        "topic_building_count",
        {"attribute_keys": ["height", "house-number"]},
    ),
    (
        "attribute-completeness",
        "topic_building_count",
        {"attribute_filter": "height=*", "attribute_title": "Height"},
    ),
    (
        "attribute-completeness",
        "topic_custom",
        {
            "attribute_filter": "drinking_water=no",
            "attribute_title": "No drinking water",
        },
    ),
    ("roads-thematic-accuracy", "topic_roads", {}),
    (
        "roads-thematic-accuracy",
        "topic_roads",
        {"attribute": "surface"},
    ),
]


@asyncpg_recorder.use_cassette
@pytest.mark.asyncio
@pytest.mark.parametrize("indicator_key,topic,kwargs", PARAMETERS)
@oqapi_vcr.use_cassette
async def test_create_indicator_public_feature_collection_single(
    bpolys,
    indicator_key,
    topic,
    kwargs,
    request,
):
    """Test create indicators for a feature collection with one feature."""
    topic = request.getfixturevalue(topic)
    indicators = await main.create_indicator(indicator_key, bpolys, topic, **kwargs)
    assert len(indicators) == 1
    for indicator in indicators:
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@oqapi_vcr.use_cassette
def test_create_indicator_public_feature_collection_multi(
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
    topic_building_count,
):
    """Test create indicators for a feature collection with multiple features."""
    indicators = asyncio.run(
        main.create_indicator(
            "mapping-saturation",
            feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
            topic_building_count,
        )
    )
    assert len(indicators) == 3
    for indicator in indicators:
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@asyncpg_recorder.use_cassette
@pytest.mark.asyncio
@pytest.mark.parametrize("indicator_key,topic,kwargs", PARAMETERS)
@oqapi_vcr.use_cassette
async def test_create_indicator_private_feature(
    feature,
    indicator_key,
    topic,
    kwargs,
    request,
):
    """Test private method to create a single indicator for a single feature."""
    topic = request.getfixturevalue(topic)
    indicator = await main._create_indicator(indicator_key, feature, topic, **kwargs)
    assert indicator.result.label is not None
    assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.result.figure is not None


@oqapi_vcr.use_cassette
def test_create_indicator_private_include_figure(bpolys, topic_building_count):
    feature = bpolys["features"][0]
    indicator = asyncio.run(
        main._create_indicator(
            "mapping-saturation",
            feature,
            topic_building_count,
            include_figure=False,
        )
    )
    assert indicator.result.figure is None
