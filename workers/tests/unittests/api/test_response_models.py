import pytest
from pydantic import ValidationError

from ohsome_quality_analyst import __version__
from ohsome_quality_analyst.api.response_models import (
    IndicatorMetadataListResponse,
    IndicatorMetadataResponse,
    ResponseBase,
    TopicListResponse,
    TopicResponse,
)
from ohsome_quality_analyst.definitions import ATTRIBUTION_URL


def test_base():
    response = ResponseBase()
    assert response.api_version == __version__
    assert response.attribution == {"url": ATTRIBUTION_URL}


def test_metadata_topics(topic_building_count):
    response = TopicResponse(result=topic_building_count)
    assert response.result == topic_building_count


def test_metadata_topics_fail():
    with pytest.raises(ValidationError):
        TopicResponse(result="")
    with pytest.raises(ValidationError):
        TopicResponse(result="bar")
    with pytest.raises(ValidationError):
        TopicResponse(result={})
    with pytest.raises(ValidationError):
        TopicResponse(result={"foo": "bar"})


def test_metadata_topics_list(topics):
    response = TopicListResponse(result=topics)
    assert response.result == topics


def test_metadata_indicators(indicator_metadata_minimal):
    response = IndicatorMetadataResponse(result=indicator_metadata_minimal)
    assert response.result == indicator_metadata_minimal


def test_metadata_indicators_fail():
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result="")
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result="bar")
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result={})
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result={"foo": "bar"})


def test_metadata_indicators_list(indicators_metadata):
    response = IndicatorMetadataListResponse(result=indicators_metadata)
    assert response.result == indicators_metadata
