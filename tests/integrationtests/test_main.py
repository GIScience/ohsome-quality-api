import asyncio
from unittest import mock

import pytest

from ohsome_quality_api import main
from tests.integrationtests.utils import oqapi_vcr


@oqapi_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "topic_minimal"),
        ("mapping-saturation", "topic_building_count"),
        ("currentness", "topic_building_count"),
    ],
)
def test_create_indicator_public_feature_collection_single(
    bpolys,
    indicator,
    topic,
    request,
):
    """Test create indicators for a feature collection with one feature."""
    topic = request.getfixturevalue(topic)
    indicators = asyncio.run(main.create_indicator(indicator, bpolys, topic))
    assert len(indicators) == 1
    for indicator in indicators:
        assert indicator.result.label is not None
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


@oqapi_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "topic_minimal"),
        ("mapping-saturation", "topic_building_count"),
        ("currentness", "topic_building_count"),
    ],
)
def test_create_indicator_private_feature(feature, indicator, topic, request):
    """Test private method to create a single indicator for a single feature."""
    topic = request.getfixturevalue(topic)
    indicator = asyncio.run(main._create_indicator(indicator, feature, topic))
    assert indicator.result.label is not None
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


@oqapi_vcr.use_cassette
def test_create_indicator_public_feature_collection_single_attribute_completeness(
    bpolys, topic_building_count, attribute_key
):
    indicators = asyncio.run(
        main.create_indicator(
            "attribute-completeness",
            bpolys,
            topic_building_count,
            attribute_keys=attribute_key,
        )
    )
    assert len(indicators) == 1
    for indicator in indicators:
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@oqapi_vcr.use_cassette
def test_create_indicator_public_feature_collection_multi_attribute_completeness(
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
    topic_building_count,
    attribute_key,
):
    """Test create indicators for a feature collection with multiple features."""
    indicators = asyncio.run(
        main.create_indicator(
            "attribute-completeness",
            feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
            topic_building_count,
            attribute_keys=attribute_key,
        )
    )
    assert len(indicators) == 3
    for indicator in indicators:
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@oqapi_vcr.use_cassette
def test_create_indicator_private_feature_attribute_completeness(
    feature, topic_building_count, attribute_key
):
    indicator = asyncio.run(
        main._create_indicator(
            "attribute-completeness",
            feature,
            topic_building_count,
            attribute_keys=attribute_key,
        )
    )
    assert indicator.result.label is not None
    assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.result.figure is not None
