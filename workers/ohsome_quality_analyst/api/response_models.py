from pydantic import BaseModel

from ohsome_quality_analyst import __version__
from ohsome_quality_analyst.definitions import ATTRIBUTION_URL
from ohsome_quality_analyst.indicators.models import IndicatorMetadata
from ohsome_quality_analyst.reports.models import ReportMetadata
from ohsome_quality_analyst.topics.models import TopicDefinition
from ohsome_quality_analyst.utils.helper import snake_to_hyphen


class ResponseBase(BaseModel):
    api_version: str = __version__
    attribution: dict[str, str] = {"url": ATTRIBUTION_URL}

    class Config:
        alias_generator = snake_to_hyphen
        frozen = True
        extra = "forbid"


class TopicResponse(ResponseBase):
    result: TopicDefinition


class TopicListResponse(ResponseBase):
    result: list[TopicDefinition]


class IndicatorMetadataResponse(ResponseBase):
    result: IndicatorMetadata


class IndicatorMetadataListResponse(ResponseBase):
    result: list[IndicatorMetadata]


class ReportMetadataResponse(ResponseBase):
    result: ReportMetadata


class ReportMetadataListResponse(ResponseBase):
    result: list[ReportMetadata]


class MetadataResponse(ResponseBase):
    class MetadataResultSchema(BaseModel):
        indicators: list[IndicatorMetadata]
        reports: list[ReportMetadata]
        topics: list[TopicDefinition]

    result: MetadataResultSchema
