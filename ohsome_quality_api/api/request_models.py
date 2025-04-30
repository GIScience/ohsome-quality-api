from typing import Dict, List, Self

import geojson
from geojson_pydantic import Feature, FeatureCollection, MultiPolygon, Polygon
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from ohsome_quality_api.api.request_context import RequestContext, request_context
from ohsome_quality_api.attributes.definitions import AttributeEnum, get_attributes
from ohsome_quality_api.indicators.definitions import get_valid_indicators
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


class BaseRequestContext(BaseModel):
    @property
    def request_context(self) -> RequestContext | None:
        return request_context.get()


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
    def transform_bpolys(cls, value) -> geojson.FeatureCollection:
        # NOTE: `geojson_pydantic` library is used only for validation and openAPI-spec
        # generation. To avoid refactoring all code the FeatureCollection object of
        # the `geojson` library is still used every else.
        return geojson.loads(value.model_dump_json())


class IndicatorRequest(BaseBpolys, BaseRequestContext):
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

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self) -> Self:
        indicator = self.request_context.path_parameters["key"]
        valid_indicators = get_valid_indicators(self.topic.key)
        if indicator not in valid_indicators:
            raise ValueError(
                "Invalid combination of indicator and topic: {} and {}".format(
                    indicator, self.topic.key
                )
            )
        return self


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

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self) -> Self:
        # NOTE: overrides parent validator. That is because endpoint of
        # indicator/attribute-completeness is fixed and therefore path parameters of
        # request context empty
        valid_indicators = get_valid_indicators(self.topic.key)
        if "attribute-completeness" not in valid_indicators:
            raise ValueError(
                "Invalid combination of indicator and topic: {} and {}".format(
                    "attribute-completeness",
                    self.topic.key,
                )
            )
        return self

    @model_validator(mode="after")
    def validate_attributes(self) -> Self:
        valid_attributes = tuple(get_attributes()[self.topic.key].keys())
        for attribute in self.attribute_keys:
            if attribute not in valid_attributes:
                raise ValueError(
                    (
                        "Invalid combination of attribute {} and topic {}. "
                        "Topic {} supports these attributes: {}"
                    ).format(
                        attribute,
                        self.topic.key,
                        self.topic.key,
                        ", ".join(valid_attributes),
                    )
                )
        return self


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

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self) -> Self:
        # NOTE: overrides parent validator. That is because endpoint of
        # indicator/attribute-completeness is fixed and therefore path parameters of
        # request context empty
        valid_indicators = get_valid_indicators(self.topic.key)
        if "attribute-completeness" not in valid_indicators:
            raise ValueError(
                "Invalid combination of indicator and topic: {} and {}".format(
                    "attribute-completeness",
                    self.topic.key,
                )
            )
        return self


class CorineComparisonRequest(IndicatorRequest):
    # TODO: possible input values restrict to actual classes (eg. 1 is
    # invalid)
    corine_class: int | None = Field(
        default=None,
        title="CORINE Land Cover class",
        description="CORINE Land Cover is a pan-European land cover inventory with thematic classes",  # noqa
    )


class IndicatorDataRequest(BaseBpolys):
    """Model for the `/indicators/mapping-saturation/data` endpoint.

    The Topic consists of name, description and data.
    """

    topic: TopicData = Field(..., title="Topic", alias="topic")
    include_figure: bool = True
    include_data: bool = False
