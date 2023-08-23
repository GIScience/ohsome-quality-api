import asyncio
from unittest import mock

import pytest
from geojson_pydantic import FeatureCollection as PydanticFeatureCollection

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.topics.models import TopicData
from tests.integrationtests.utils import oqt_vcr


@oqt_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "topic_minimal"),
        ("mapping-saturation", "topic_building_count"),
        ("currentness", "topic_building_count"),
        ("attribute-completeness", "topic_building_count"),
    ],
)
def test_create_indicator_public_feature_collection_single(
    pydantic_bpolys,
    indicator,
    topic,
    request,
):
    """Test create indicators for a feature collection with one feature."""
    topic = request.getfixturevalue(topic)
    indicators = asyncio.run(oqt.create_indicator(indicator, pydantic_bpolys, topic))
    assert len(indicators) == 1
    for indicator in indicators:
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@oqt_vcr.use_cassette
def test_create_indicator_public_feature_collection_multi(
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
    topic_minimal,
):
    """Test create indicators for a feature collection with multiple features."""
    indicators = asyncio.run(
        oqt.create_indicator(
            "minimal",
            PydanticFeatureCollection(
                **feature_collection_heidelberg_bahnstadt_bergheim_weststadt
            ),
            topic_minimal,
        )
    )
    assert len(indicators) == 3
    for indicator in indicators:
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.figure is not None


@oqt_vcr.use_cassette
@pytest.mark.parametrize(
    "indicator,topic",
    [
        ("minimal", "topic_minimal"),
        ("mapping-saturation", "topic_building_count"),
        ("currentness", "topic_building_count"),
        ("attribute-completeness", "topic_building_count"),
    ],
)
def test_create_indicator_private_feature(feature, indicator, topic, request):
    """Test private method to create a single indicator for a single feature."""
    topic = request.getfixturevalue(topic)
    indicator = asyncio.run(oqt._create_indicator(indicator, feature, topic))
    assert indicator.result.label is not None
    assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.result.figure is not None


@oqt_vcr.use_cassette
def test_create_indicator_private_include_figure(bpolys, topic_minimal):
    indicator = asyncio.run(
        oqt._create_indicator(
            "minimal",
            bpolys,
            topic_minimal,
            include_figure=False,
        )
    )
    assert indicator.result.figure is None


@oqt_vcr.use_cassette
def test_create_report_private(feature):
    """Minimal viable request for a single bpoly."""
    report = asyncio.run(oqt._create_report("minimal", feature))
    assert report.result.label is not None
    assert report.result.class_ is not None
    assert report.result.description is not None


@mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqt_vcr.use_cassette
def test_create_indicator_size_limit_bpolys(pydantic_bpolys, topic_minimal):
    with pytest.raises(ValueError):
        asyncio.run(oqt.create_indicator("minimal", pydantic_bpolys, topic_minimal))


@mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqt_vcr.use_cassette
def test_create_indicator_size_limit_bpolys_ms(pydantic_bpolys, topic_building_count):
    # Size limit is disabled for the Mapping Saturation indicator.
    asyncio.run(
        oqt.create_indicator(
            "mapping-saturation", pydantic_bpolys, topic_building_count
        )
    )


@mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqt_vcr.use_cassette
def test_create_indicator_size_limit_bpolys_data(pydantic_bpolys):
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
    asyncio.run(oqt.create_indicator("mapping-saturation", pydantic_bpolys, topic))
