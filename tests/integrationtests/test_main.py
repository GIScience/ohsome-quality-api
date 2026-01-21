import asyncio
from unittest import mock

import asyncpg_recorder
import pytest

from ohsome_quality_api import main
from ohsome_quality_api.topics.models import TopicData
from tests.integrationtests.utils import oqapi_vcr


@asyncpg_recorder.use_cassette
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "indicator_key,topic,kwargs",
    [
        ("minimal", "topic_minimal", {}),
        ("mapping-saturation", "topic_building_count", {}),
        ("currentness", "topic_building_count", {}),
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
        ("roads-thematic-accuracy", "topic_roads", {}),
        (
            "roads-thematic-accuracy",
            "topic_roads",
            {"attribute": "surface"},
        ),
    ],
)
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
        if indicator_key == "roads-thematic-accuracy":
            assert indicator.result.value is None
        else:
            assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@oqapi_vcr.use_cassette
def test_create_indicator_public_feature_collection_multi(
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
    topic_minimal,
):
    """Test create indicators for a feature collection with multiple features."""
    indicators = asyncio.run(
        main.create_indicator(
            "minimal",
            feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
            topic_minimal,
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
@pytest.mark.parametrize(
    "indicator_key,topic,kwargs",
    [
        ("minimal", "topic_minimal", {}),
        ("mapping-saturation", "topic_building_count", {}),
        ("currentness", "topic_building_count", {}),
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
        ("roads-thematic-accuracy", "topic_roads", {}),
        (
            "roads-thematic-accuracy",
            "topic_roads",
            {"attribute": "surface"},
        ),
    ],
)
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
    if indicator_key == "roads-thematic-accuracy":
        assert indicator.result.value is None
    else:
        assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.result.figure is not None


@oqapi_vcr.use_cassette
def test_create_indicator_private_include_figure(bpolys, topic_minimal):
    indicator = asyncio.run(
        main._create_indicator(
            "minimal",
            bpolys,
            topic_minimal,
            include_figure=False,
        )
    )
    assert indicator.result.figure is None


@mock.patch.dict("os.environ", {"OQAPI_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqapi_vcr.use_cassette
def test_create_indicator_size_limit_bpolys(bpolys, topic_minimal):
    with pytest.raises(ValueError):
        asyncio.run(main.create_indicator("minimal", bpolys, topic_minimal))


@mock.patch.dict("os.environ", {"OQAPI_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqapi_vcr.use_cassette
def test_create_indicator_size_limit_bpolys_ms(bpolys, topic_building_count):
    # Size limit is disabled for the Mapping Saturation indicator.
    asyncio.run(
        main.create_indicator("mapping-saturation", bpolys, topic_building_count)
    )


@mock.patch.dict("os.environ", {"OQAPI_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqapi_vcr.use_cassette
def test_create_indicator_size_limit_bpolys_data(bpolys):
    # Size limit is disabled for request with custom data.
    topic = TopicData(
        key="key",
        name="name",
        description="description",
        data={
            "result": [
                {
                    "value": 1.0,
                    "timestamp": "2020-03-20T01:30:08.180856",
                }
            ]
        },
    )
    asyncio.run(main.create_indicator("mapping-saturation", bpolys, topic))
