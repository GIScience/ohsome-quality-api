from typing import Literal

from geojson_pydantic import Feature, FeatureCollection, MultiPolygon, Polygon
from pydantic import BaseModel, ConfigDict, field_validator

from ohsome_quality_api import __version__
from ohsome_quality_api.definitions import ATTRIBUTION_URL
from ohsome_quality_api.indicators.definitions import IndicatorEnum
from ohsome_quality_api.indicators.models import Result as IndicatorResult
from ohsome_quality_api.projects.definitions import ProjectEnum
from ohsome_quality_api.projects.models import Project
from ohsome_quality_api.quality_dimensions.definitions import QualityDimensionEnum
from ohsome_quality_api.quality_dimensions.models import QualityDimension
from ohsome_quality_api.reports.definitions import ReportEnum
from ohsome_quality_api.reports.models import ReportMetadata
from ohsome_quality_api.topics.definitions import TopicEnum
from ohsome_quality_api.utils.helper import snake_to_lower_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )


class BaseResponse(BaseConfig):
    api_version: str = __version__
    attribution: dict[str, str] = {"url": ATTRIBUTION_URL}


class TopicMetadata(BaseConfig):
    name: str
    description: str
    endpoint: Literal["elements"]
    aggregation_type: Literal["area", "count", "length", "perimeter"]
    filter: str
    indicators: list[str]
    projects: list[ProjectEnum]
    source: str | None = None
    model_config = ConfigDict(title="Topic Metadata")


class TopicMetadataResponse(BaseResponse):
    result: dict[str, TopicMetadata]

    @field_validator("result")
    @classmethod
    def check_topic_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            TopicEnum(key)
        return value


class AttributeMetadata(BaseConfig):
    name: str
    description: str
    filter: str
    model_config = ConfigDict(title="Attribute Metadata")


class AttributeMetadataResponse(BaseResponse):
    result: dict[str, AttributeMetadata]

    @field_validator("result")
    @classmethod
    def check_topic_dict(cls, value):
        assert len(value) > 0
        return value


class QualityDimensionMetadataResponse(BaseResponse):
    result: dict[str, QualityDimension]

    @field_validator("result")
    @classmethod
    def check_quality_dimension_dict(cls, values):
        assert len(values) > 0
        for key in values.keys():
            QualityDimensionEnum(key)
        return values


class ProjectMetadataResponse(BaseResponse):
    result: dict[str, Project]

    @field_validator("result")
    @classmethod
    def check_project_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            ProjectEnum(key)
        return value


class IndicatorMetadata(BaseConfig):
    name: str
    description: str
    projects: list[ProjectEnum]
    quality_dimension: QualityDimensionEnum
    model_config = ConfigDict(title="Indicator Metadata")


class IndicatorMetadataResponse(BaseResponse):
    result: dict[str, IndicatorMetadata]

    @field_validator("result")
    @classmethod
    def check_indicator_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            IndicatorEnum(key)
        return value


class IndicatorMetadataCoverageResponse(
    BaseResponse,
    FeatureCollection[Feature[Polygon | MultiPolygon, dict]],
):
    model_config = ConfigDict(title="Indicator Coverage", extra="allow")


class ReportMetadataResponse(BaseResponse):
    result: dict[str, ReportMetadata]

    @field_validator("result")
    @classmethod
    def check_report_dict(cls, value):
        assert len(value) > 0
        for key in value.keys():
            ReportEnum(key)
        return value


class Metadata(BaseConfig):
    indicators: dict[str, IndicatorMetadata]
    topics: dict[str, TopicMetadata]
    quality_dimensions: dict[str, QualityDimension]
    projects: dict[str, Project]
    model_config = ConfigDict(title="Metadata")


class MetadataResponse(BaseResponse):
    result: Metadata


class TopicProperties(TopicMetadata):
    key: TopicEnum


class CompIndicator(BaseConfig):
    # Indicator model for composition in response models.
    metadata: IndicatorMetadata
    topic: TopicProperties
    result: IndicatorResult
    model_config = ConfigDict(extra="allow")  # indicators can include extra attributes


class IndicatorJSONResponse(BaseResponse):
    result: list[CompIndicator]
    model_config = ConfigDict(extra="allow")


class IndicatorGeoJSONResponse(
    BaseResponse,
    FeatureCollection[Feature[Polygon | MultiPolygon, CompIndicator]],
):
    model_config = ConfigDict(extra="allow")
