import pytest
from approvaltests import verify
from pydantic import ValidationError

from ohsome_quality_api import __version__
from ohsome_quality_api.api.response_models import (
    BaseResponse,
    IndicatorMetadata,
    IndicatorMetadataCoverageResponse,
    IndicatorMetadataResponse,
    ProjectMetadataResponse,
    QualityDimensionMetadataResponse,
    TopicMetadata,
    TopicMetadataResponse,
)
from ohsome_quality_api.definitions import ATTRIBUTION_URL
from ohsome_quality_api.topics.definitions import get_topic_preset
from tests.approvaltests_namers import PytestNamer


def test_base():
    response = BaseResponse()
    assert response.api_version == __version__
    assert response.attribution == {"url": ATTRIBUTION_URL}


def test_topic_metadata():
    TopicMetadata(
        name="foo",
        description="foo",
        endpoint="elements",
        aggregation_type="area",
        filter="foo",
        indicators=["mapping-saturation"],
        projects=["core"],
        source=None,
    )


def test_topic_metadata_response():
    TopicMetadataResponse(
        result={
            "building-count": TopicMetadata(
                name="foo",
                description="foo",
                endpoint="elements",
                aggregation_type="area",
                filter="foo",
                indicators=["mapping-saturation"],
                projects=["core"],
                source=None,
            )
        }
    )


def test_topic_metadata_response_fail(topic_building_count):
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


def test_topic_metadata_translated(locale_de):
    topic = get_topic_preset("building-count")
    topic = topic.model_dump()
    topic.pop("key")
    topic.pop("ratio_filter")
    topic = TopicMetadata(**topic)
    verify(topic.model_dump_json(indent=2), namer=PytestNamer())


def test_metadata_quality_dimensions(metadata_quality_dimension_completeness):
    response = QualityDimensionMetadataResponse(
        result=metadata_quality_dimension_completeness
    )
    assert response.result == metadata_quality_dimension_completeness


def test_metadata_quality_dimensions_fail(quality_dimension_completeness):
    with pytest.raises(ValidationError):
        QualityDimensionMetadataResponse(result="")
    with pytest.raises(ValidationError):
        QualityDimensionMetadataResponse(result="bar")
    with pytest.raises(ValidationError):
        QualityDimensionMetadataResponse(result={})
    with pytest.raises(ValidationError):
        QualityDimensionMetadataResponse(result={"foo": "bar"})
    with pytest.raises(ValidationError):
        QualityDimensionMetadataResponse(result={"foo": quality_dimension_completeness})


def test_metadata_quality_dimensions_list(quality_dimensions):
    response = QualityDimensionMetadataResponse(result=quality_dimensions)
    assert response.result == quality_dimensions


def test_metadata_projects(metadata_project_core):
    response = ProjectMetadataResponse(result=metadata_project_core)
    assert response.result == metadata_project_core


def test_metadata_projects_fail(project_core):
    with pytest.raises(ValidationError):
        ProjectMetadataResponse(result="")
    with pytest.raises(ValidationError):
        ProjectMetadataResponse(result="bar")
    with pytest.raises(ValidationError):
        ProjectMetadataResponse(result={})
    with pytest.raises(ValidationError):
        ProjectMetadataResponse(result={"foo": "bar"})
    with pytest.raises(ValidationError):
        ProjectMetadataResponse(result={"foo": project_core})


def test_metadata_projects_list(projects):
    response = ProjectMetadataResponse(result=projects)
    assert response.result == projects


def test_indicator_metadata():
    IndicatorMetadata(
        name="foo",
        description="foo",
        projects=["core"],
        quality_dimension="completeness",
    )


def test_indicator_metadata_response():
    IndicatorMetadataResponse(
        result={
            "mapping-saturation": IndicatorMetadata(
                name="foo",
                description="foo",
                projects=["core"],
                quality_dimension="completeness",
            )
        }
    )


def test_indicator_metadata_response_fail(metadata_indicator_minimal):
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


def test_indicator_metadata_coverage(bpolys):
    IndicatorMetadataCoverageResponse(**bpolys)
