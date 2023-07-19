import asyncio
from unittest import mock

import pytest

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
def test_create_indicator(bpolys, indicator, topic, request):
    """Minimal viable request for a single bpoly."""
    topic = request.getfixturevalue(topic)
    indicators = asyncio.run(oqt.create_indicator(indicator, bpolys, topic))
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
def test__create_indicator(feature, indicator, topic, request):
    """Minimal viable request for a single bpoly."""
    topic = request.getfixturevalue(topic)
    indicator = asyncio.run(oqt._create_indicator(indicator, feature, topic))
    assert indicator.result.label is not None
    assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.result.figure is not None


@oqt_vcr.use_cassette
def test__create_report(feature):
    """Minimal viable request for a single bpoly."""
    report = asyncio.run(oqt._create_report("minimal", feature))
    assert report.result.label is not None
    assert report.result.class_ is not None
    assert report.result.description is not None


@mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
def test_create_indicator_size_limit_bpolys(bpolys, topic_minimal):
    with pytest.raises(ValueError):
        asyncio.run(oqt.create_indicator("minimal", bpolys, topic_minimal))


@mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
@oqt_vcr.use_cassette
def test_create_indicator_size_limit_bpolys_ms(bpolys, topic_building_count):
    """Size limit is disabled for the Mapping Saturation indicator.

    Test that no error gets raised.
    """
    asyncio.run(
        oqt.create_indicator("mapping-saturation", bpolys, topic_building_count)
    )


@mock.patch.dict("os.environ", {"OQT_GEOM_SIZE_LIMIT": "1"}, clear=True)
def test_create_indicator_size_limit_topic_data(bpolys):
    """Size limit is disabled for request with custom data.

    Test that no error gets raised.
    """
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
    asyncio.run(oqt.create_indicator("mapping-saturation", bpolys, topic))
