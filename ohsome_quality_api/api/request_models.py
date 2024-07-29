import json

import geojson
from geojson import FeatureCollection
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ohsome_quality_api.topics.definitions import TopicEnum
from ohsome_quality_api.topics.models import TopicData
from ohsome_quality_api.utils.helper import snake_to_lower_camel
from ohsome_quality_api.utils.validators import validate_geojson


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        populate_by_name=True,
        frozen=True,
        extra="forbid",
    )


class BaseBpolys(BaseConfig):
    bpolys: dict = Field(
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
                },
            ],
        }
    )

    @field_validator("bpolys")
    @classmethod
    def validate_bpolys(cls, value) -> FeatureCollection:
        obj = geojson.loads(json.dumps(value))
        if not isinstance(obj, FeatureCollection):
            raise ValueError("must be of type FeatureCollection")
        validate_geojson(obj)  # Check if exceptions are raised
        return obj


class IndicatorRequest(BaseBpolys):
    topic_key: TopicEnum = Field(
        ...,
        title="Topic Key",
        alias="topic",
    )
    attribute_key: str = Field(
        ...,
        title="Attribute Key",
        alias="attribute",
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
