from geojson_pydantic import Feature, FeatureCollection, MultiPolygon, Polygon
from pydantic import BaseModel, ConfigDict, Field

from ohsome_quality_api.topics.definitions import TopicEnum
from ohsome_quality_api.topics.models import TopicData
from ohsome_quality_api.utils.helper import snake_to_lower_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        populate_by_name=True,
        frozen=True,
        extra="forbid",
    )


class BaseBpolys(BaseConfig):
    bpolys: FeatureCollection[Feature[Polygon | MultiPolygon]]


class IndicatorRequest(BaseBpolys):
    topic_key: TopicEnum = Field(
        ...,
        title="Topic Key",
        alias="topic",
    )
    include_figure: bool = True


class IndicatorDataRequest(BaseBpolys):
    """Model for the `/indicators/mapping-saturation/data` endpoint.

    The Topic consists of name, description and data.
    """

    topic: TopicData = Field(..., title="Topic", alias="topic")
    include_figure: bool = True
    include_data: bool = False


class ReportRequest(BaseBpolys):
    pass
    # include_data: bool = False
