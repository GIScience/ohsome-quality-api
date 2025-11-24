from enum import Enum

import geojson
from fastapi_i18n import _
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
from ohsome_quality_api.config import get_config_value
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


FeatureCollection_ = FeatureCollection[Feature[Polygon | MultiPolygon, dict]]


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
    ohsomedb: bool | str = False

    @field_validator("topic")
    @classmethod
    def transform_topic(cls, value) -> TopicDefinition:
        return get_topic_preset(value.value)

    @field_validator("ohsomedb")
    @classmethod
    def transform_ohsomedb(cls, value) -> bool:
        # TODO: Feature Flag
        if get_config_value("ohsomedb_enabled") is False:
            return False

        if isinstance(value, str):
            if value == "true":
                return True
            else:
                return False
        else:
            return value

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self):
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
    attribute_keys: list[AttributeEnum] = Field(
        ...,
        title="Attribute Keys",
        alias="attributes",
    )

    @field_validator("attribute_keys")
    @classmethod
    def transform_attributes(cls, value) -> list[str]:
        return [attribute.value for attribute in value]

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self):
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
    def validate_attributes(self):
        valid_attributes = tuple(get_attributes()[self.topic.key].keys())
        for attribute in self.attribute_keys:
            if attribute not in valid_attributes:
                raise ValueError(
                    "Invalid combination of attribute {} and topic {}. "
                    "Topic {} supports these attributes: {}".format(
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
        description=_("ohsome filter query representing custom attributes."),
    )
    attribute_title: str = Field(
        ...,
        title="Attribute Title",
        description=(
            _("Title describing the attributes represented by the Attribute Filter.")
        ),
    )

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self):
        # NOTE: overrides parent validator. That is because endpoint of
        # indicator/attribute-completeness is fixed and therefore path parameters of
        # request context empty
        valid_indicators = get_valid_indicators(self.topic.key)
        if "attribute-completeness" not in valid_indicators:
            raise ValueError(
                "Invalid combination of indicator and topic: {} and {}"
            ).format(
                "attribute-completeness",
                self.topic.key,
            )
        return self


class CorineLandCoverClassLevel1(Enum):
    ARTIFICIAL_AREAS = "1"
    AGRICULTURAL_AREAS = "2"
    FOREST_AND_SEMINATURAL_AREAS = "3"
    WETLANDS = "4"
    WATER_BODIES = "5"


class CorineLandCoverClass(Enum):
    """Corine Land Cover Class Level 2."""

    # TODO: Use more descriptive names
    ARTIFICIAL_AREAS_1 = "11"
    ARTIFICIAL_AREAS_2 = "12"
    ARTIFICIAL_AREAS_3 = "13"
    ARTIFICIAL_AREAS_4 = "14"
    AGRICULTURAL_AREAS_1 = "21"
    AGRICULTURAL_AREAS_2 = "22"
    AGRICULTURAL_AREAS_3 = "23"
    AGRICULTURAL_AREAS_4 = "24"
    FOREST_AND_SEMINATURAL_AREAS_1 = "31"
    FOREST_AND_SEMINATURAL_AREAS_2 = "32"
    FOREST_AND_SEMINATURAL_AREAS_3 = "33"
    WETLANDS_1 = "41"
    WETLANDS_2 = "42"
    WATER_BODIES_1 = "51"
    WATER_BODIES_2 = "52"


class LandCoverThematicAccuracyRequest(IndicatorRequest):
    corine_land_cover_class: CorineLandCoverClass | None = Field(
        default=None,
        title="CORINE Land Cover class",
        description=_(
            "CORINE Land Cover is a pan-European land cover"
            " inventory with thematic classes."
        ),  # noqa
    )

    @field_validator("corine_land_cover_class", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def validate_indicator_topic_combination(self):
        # NOTE: overrides parent validator. That is because endpoint of
        # indicator/land-cover-thematic-accuracy is fixed and therefore path
        # parameters of request context are empty
        valid_indicators = get_valid_indicators(self.topic.key)
        if "land-cover-thematic-accuracy" not in valid_indicators:
            raise ValueError(
                "Invalid combination of indicator and topic: {} and {}".format(
                    "land-cover-thematic-accuracy",
                    self.topic.key,
                )
            )
        return self


class IndicatorDataRequest(BaseBpolys):
    """Model for the `/indicators/mapping-saturation/data` endpoint.

    The Topic consists of name, description and data.
    """

    topic: TopicData = Field(..., title="Topic", alias="topic")
    include_figure: bool = True
    include_data: bool = False
