"""Pydantic models of API responses."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

from ohsome_quality_analyst import __version__
from ohsome_quality_analyst.definitions import ATTRIBUTION_URL
from ohsome_quality_analyst.indicators.definitions import IndicatorEnum
from ohsome_quality_analyst.projects.definitions import ProjectEnum
from ohsome_quality_analyst.projects.models import Project
from ohsome_quality_analyst.quality_dimensions.definitions import QualityDimensionEnum
from ohsome_quality_analyst.quality_dimensions.models import QualityDimension
from ohsome_quality_analyst.reports.definitions import ReportEnum
from ohsome_quality_analyst.reports.models import ReportMetadata
from ohsome_quality_analyst.topics.definitions import TopicEnum
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel


class ResponseBase(BaseModel):
    api_version: str = __version__
    attribution: dict[str, str] = {"url": ATTRIBUTION_URL}
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )


class TopicMetadata(BaseModel):
    name: str
    description: str
    endpoint: Literal["elements"]
    aggregation_type: Literal["area", "count", "length", "perimeter"]
    filter: str
    indicators: list[str]
    projects: list[ProjectEnum]
    source: str | None = None
    model_config = ConfigDict(title="Topic Metadata")


class TopicMetadataResponse(ResponseBase):
    result: dict[str, TopicMetadata]

    @field_validator("result")
    @classmethod
    def check_topic_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            TopicEnum(key)
        return value


class QualityDimensionMetadataResponse(ResponseBase):
    result: dict[str, QualityDimension]

    @field_validator("result")
    @classmethod
    def check_quality_dimension_dict(cls, values):
        assert len(values) > 0
        for key in values.keys():
            QualityDimensionEnum(key)
        return values


class ProjectMetadataResponse(ResponseBase):
    result: dict[str, Project]

    @field_validator("result")
    @classmethod
    def check_project_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            ProjectEnum(key)
        return value


class IndicatorMetadata(BaseModel):
    name: str
    description: str
    projects: list[ProjectEnum]
    quality_dimension: QualityDimensionEnum
    model_config = ConfigDict(title="Indicator Metadata")


class IndicatorMetadataResponse(ResponseBase):
    result: dict[str, IndicatorMetadata]

    @field_validator("result")
    @classmethod
    def check_indicator_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            IndicatorEnum(key)
        return value


class ReportMetadataResponse(ResponseBase):
    result: dict[str, ReportMetadata]

    @field_validator("result")
    @classmethod
    def check_report_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            ReportEnum(key)
        return value


class Metadata(BaseModel):
    indicators: dict[str, IndicatorMetadata]
    topics: dict[str, TopicMetadata]
    quality_dimensions: dict[str, QualityDimension]
    projects: dict[str, Project]
    model_config = ConfigDict(title="Metadata")


class MetadataResponse(ResponseBase):
    result: Metadata
