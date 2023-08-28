import pytest

from ohsome_quality_analyst.api.request_models import (
    IndicatorDataRequest,
)


def test_indicator_data(feature_collection_germany_heidelberg):
    topic = {"key": "foo", "name": "bar", "description": "buz", "data": {}}
    IndicatorDataRequest(
        bpolys=feature_collection_germany_heidelberg.model_dump(),
        topic=topic,
    )


def test_topic_data_valid(feature_collection_germany_heidelberg):
    topic = {
        "key": "foo",
        "name": "bar",
        "description": "buz",
        "data": {},
    }
    IndicatorDataRequest(
        bpolys=feature_collection_germany_heidelberg.model_dump(), topic=topic
    )


def test_topic_data_invalid(feature_collection_germany_heidelberg):
    for topic in (
        {"key": "foo", "name": "bar", "data": {}},
        {"key": "foo", "description": "bar", "data": {}},
        {"key": "foo", "name": "bar", "description": "buz"},
        {"key": "foo", "name": "bar", "description": "buz", "data": "fis"},
    ):
        with pytest.raises(ValueError):
            IndicatorDataRequest(
                bpolys=feature_collection_germany_heidelberg.model_dump(), topic=topic
            )
