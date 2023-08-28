import pytest

from ohsome_quality_api.api.request_models import (
    IndicatorDataRequest,
)


def test_indicator_data(bpolys):
    topic = {"key": "foo", "name": "bar", "description": "buz", "data": {}}
    IndicatorDataRequest(
        bpolys=bpolys,
        topic=topic,
    )
    IndicatorDataRequest(bpolys=bpolys, topic=topic)


def test_topic_data_valid(bpolys):
    topic = {
        "key": "foo",
        "name": "bar",
        "description": "buz",
        "data": {},
    }
    IndicatorDataRequest(bpolys=bpolys, topic=topic)


def test_topic_data_invalid(bpolys):
    for topic in (
        {"key": "foo", "name": "bar", "data": {}},
        {"key": "foo", "description": "bar", "data": {}},
        {"key": "foo", "name": "bar", "description": "buz"},
        {"key": "foo", "name": "bar", "description": "buz", "data": "fis"},
    ):
        with pytest.raises(ValueError):
            IndicatorDataRequest(bpolys=bpolys, topic=topic)
