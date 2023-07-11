"""Data models of the API request body.

This module uses the library `pydantic` for data validation and
settings management using Python type hinting.

Besides data validation through `pydantic`, `FastAPI` will display additional
information derived from `pydantic` models in the automatic generated API documentation.
"""

import json
from enum import Enum

import geojson
import pydantic
from geojson import Feature, FeatureCollection
from pydantic import BaseModel

from ohsome_quality_analyst.definitions import (
    get_dataset_names,
    get_fid_fields,
    get_indicator_names,
    get_report_names,
    get_topic_keys,
)
from ohsome_quality_analyst.topics.models import TopicData
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel
from ohsome_quality_analyst.utils.validators import validate_geojson

IndicatorEnum = Enum("IndicatorEnum", {name: name for name in get_indicator_names()})
ReportEnum = Enum("ReportEnum", {name: name for name in get_report_names()})
TopicEnum = Enum("TopicEnum", {name: name for name in get_topic_keys()})
DatasetEnum = Enum("DatasetNames", {name: name for name in get_dataset_names()})
FidFieldEnum = Enum("FidFieldEnum", {name: name for name in get_fid_fields()})


class BaseIndicator(BaseModel):
    include_svg: bool = False
    include_html: bool = False
    include_data: bool = False
    flatten: bool = False

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        # Allow population by field name not just by alias name
        allow_population_by_field_name = True
        allow_mutation = False
        extra = "forbid"


class BaseReport(BaseModel):
    include_svg: bool = False
    include_html: bool = False
    include_data: bool = False
    flatten: bool = False

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        # Allow population by field name not just by alias name
        allow_population_by_field_name = True
        allow_mutation = False
        extra = "forbid"


class BaseTopicName(BaseModel):
    topic_key: TopicEnum = pydantic.Field(
        ...,
        title="Topic Key",
        alias="topic",
        example="building-count",
    )


class BaseTopicData(BaseModel):
    """Model for the parameter `topic`.

    The Topic consists of name, description and data.
    """

    topic: TopicData = pydantic.Field(..., title="Topic", alias="topic")


class BaseBpolys(BaseModel):
    """Model for the `bpolys` parameter."""

    bpolys: Feature | FeatureCollection = pydantic.Field(
        ...,
        title="bpolys",
        example={
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
    )

    @pydantic.validator("bpolys")
    @classmethod
    def validate_bpolys(cls, value) -> FeatureCollection | Feature:
        obj = geojson.loads(json.dumps(value))
        validate_geojson(obj)  # Check if exceptions are raised
        return obj


class IndicatorBpolys(BaseIndicator, BaseTopicName, BaseBpolys):
    pass


class IndicatorData(BaseIndicator, BaseTopicData, BaseBpolys):
    pass


class ReportBpolys(BaseReport, BaseBpolys):
    pass


INDICATOR_EXAMPLES = {
    "AOI": {
        "summary": "Request an Indicator for a given AOI (`bpolys`).",
        "value": {
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
        },
    },
}
