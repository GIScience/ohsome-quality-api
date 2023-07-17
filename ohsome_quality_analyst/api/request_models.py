import json

import geojson
import pydantic
from geojson import FeatureCollection
from pydantic import BaseModel

from ohsome_quality_analyst.topics.definitions import TopicEnum
from ohsome_quality_analyst.topics.models import TopicData
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel
from ohsome_quality_analyst.utils.validators import validate_geojson


class BaseBpolys(BaseModel):
    bpolys: FeatureCollection

    @pydantic.validator("bpolys")
    @classmethod
    def validate_bpolys(cls, value) -> FeatureCollection:
        obj = geojson.loads(json.dumps(value))
        if not isinstance(obj, FeatureCollection):
            raise ValueError("must be of type FeatureCollection")
        validate_geojson(obj)  # Check if exceptions are raised
        return obj


class IndicatorRequest(BaseBpolys):
    topic_key: TopicEnum = pydantic.Field(
        ...,
        title="Topic Key",
        alias="topic",
        example="building-count",
    )
    include_data: bool = False

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        # Allow population by field name not just by alias name
        allow_population_by_field_name = True
        allow_mutation = False
        extra = "forbid"
        schema_extra = {
            "examples": [
                {
                    "topic": "building-count",
                    "bpolys": {
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
                }
            ]
        }


class IndicatorDataRequest(BaseBpolys):
    """Model for the `/indicators/mapping-saturation/data` endpoint.

    The Topic consists of name, description and data.
    """

    include_data: bool = False
    topic: TopicData = pydantic.Field(..., title="Topic", alias="topic")

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        # Allow population by field name not just by alias name
        allow_population_by_field_name = True
        allow_mutation = False
        extra = "forbid"


class ReportRequest(BaseBpolys):
    include_data: bool = False

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        # Allow population by field name not just by alias name
        allow_population_by_field_name = True
        allow_mutation = False
        extra = "forbid"
