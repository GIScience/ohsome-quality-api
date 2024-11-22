from typing import Dict, List

import geojson
from geojson_pydantic import Feature, FeatureCollection, MultiPolygon, Polygon
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from ohsome_quality_api.attributes.definitions import AttributeEnum
from ohsome_quality_api.topics.definitions import TopicEnum, get_topic_preset
from ohsome_quality_api.topics.models import TopicData, TopicDefinition
from ohsome_quality_api.utils.helper import snake_to_lower_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        populate_by_name=True,
        frozen=True,
        extra="forbid",
    )


FeatureCollection_ = FeatureCollection[Feature[Polygon | MultiPolygon, Dict]]


class BaseBpolys(BaseConfig):
    bpolys: FeatureCollection_ = Field(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [8.674092292785645, 49.40427147224242],
                                [8.695850372314453, 49.40427147224242],
                                [8.695850372314453, 49.415552187316095],
                                [8.674092292785645, 49.415552187316095],
                                [8.674092292785645, 49.40427147224242],
                            ]
                        ],
                    },
                    "properties": {},
                }
            ],
        }
    )

    @field_validator("bpolys")
    @classmethod
    def transform_bpolys(cls, value):
        # NOTE: `geojson_pydantic` library is used only for validation and openAPI-spec
        # generation. To avoid refactoring all code the FeatureCollection object of
        # the `geojson` library is still used every else.
        return geojson.loads(value.model_dump_json())


class IndicatorRequest(BaseBpolys):
    topic: TopicEnum = Field(
        ...,
        title="Topic Key",
        alias="topic",
    )
    include_figure: bool = True

    @field_validator("topic")
    @classmethod
    def transform_topic(cls, value) -> TopicDefinition:
        return get_topic_preset(value.value)


class AttributeCompletenessKeyRequest(IndicatorRequest):
    attribute_keys: List[AttributeEnum] = Field(
        ...,
        title="Attribute Keys",
        alias="attributes",
    )

    @field_validator("attribute_keys")
    @classmethod
    def transform_attributes(cls, value) -> list[str]:
        return [attribute.value for attribute in value]


class AttributeCompletenessFilterRequest(IndicatorRequest):
    attribute_filter: str = Field(
        ...,
        title="Attribute Filter",
        description="ohsome filter query representing custom attributes.",
    )
    attribute_title: str = Field(
        ...,
        title="Attribute Title",
        description=(
            "Title describing the attributes represented by the Attribute Filter."
        ),
    )


class IndicatorDataRequest(BaseBpolys):
    """Model for the `/indicators/mapping-saturation/data` endpoint.

    The Topic consists of name, description and data.
    """

    topic: TopicData = Field(..., title="Topic", alias="topic")
    include_figure: bool = True
    include_data: bool = False
