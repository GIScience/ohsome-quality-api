import pytest
from pydantic import ValidationError

from ohsome_quality_analyst import __version__
from ohsome_quality_analyst.api.response_models import (
    IndicatorMetadataResponse,
    ReportMetadataResponse,
    ResponseBase,
    TopicMetadataResponse,
)
from ohsome_quality_analyst.definitions import ATTRIBUTION_URL


def test_base():
    response = ResponseBase()
    assert response.api_version == __version__
    assert response.attribution == {"url": ATTRIBUTION_URL}


def test_metadata_topics(metadata_topic_building_count):
    response = TopicMetadataResponse(result=metadata_topic_building_count)
    assert response.result == metadata_topic_building_count


def test_metadata_topics_fail(topic_building_count):
    with pytest.raises(ValidationError):
        TopicMetadataResponse(result="")
    with pytest.raises(ValidationError):
        TopicMetadataResponse(result="bar")
    with pytest.raises(ValidationError):
        TopicMetadataResponse(result={})
    with pytest.raises(ValidationError):
        TopicMetadataResponse(result={"foo": "bar"})
    with pytest.raises(ValidationError):
        TopicMetadataResponse(result={"foo": topic_building_count})


def test_metadata_topics_list(topic_definitions):
    response = TopicMetadataResponse(result=topic_definitions)
    assert response.result == topic_definitions


def test_metadata_indicators(metadata_indicator_minimal):
    response = IndicatorMetadataResponse(result=metadata_indicator_minimal)
    assert response.result == metadata_indicator_minimal


def test_metadata_indicators_fail(metadata_indicator_minimal):
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result="")
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result="bar")
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result={})
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result={"foo": "bar"})
    with pytest.raises(ValidationError):
        IndicatorMetadataResponse(result={"foo": metadata_indicator_minimal})


def test_metadata_indicators_list(indicators_metadata):
    response = IndicatorMetadataResponse(result=indicators_metadata)
    assert response.result == indicators_metadata


def test_metadata_reports(metadata_report_minimal):
    response = ReportMetadataResponse(result=metadata_report_minimal)
    assert response.result == metadata_report_minimal


def test_metadata_reports_fail(metadata_report_minimal):
    with pytest.raises(ValidationError):
        ReportMetadataResponse(result="")
    with pytest.raises(ValidationError):
        ReportMetadataResponse(result="bar")
    with pytest.raises(ValidationError):
        ReportMetadataResponse(result={})
    with pytest.raises(ValidationError):
        ReportMetadataResponse(result={"foo": "bar"})
    with pytest.raises(ValidationError):
        ReportMetadataResponse(result={"foo": metadata_report_minimal})


def test_metadata_reports_list(reports_metadata):
    response = ReportMetadataResponse(result=reports_metadata)
    assert response.result == reports_metadata
