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


class BaseDatabase(BaseModel):
    """Model for the combination of parameters: `dataset`, `feature_id`, `fid_field`."""

    dataset: DatasetEnum = pydantic.Field(..., title="Dataset Name", example="regions")
    feature_id: str = pydantic.Field(..., title="Feature Id", example="3")
    fid_field: FidFieldEnum | None = None


class IndicatorBpolys(BaseIndicator, BaseTopicName, BaseBpolys):
    pass


class IndicatorDatabase(BaseIndicator, BaseTopicName, BaseDatabase):
    pass


class IndicatorData(BaseIndicator, BaseTopicData, BaseBpolys):
    pass


class ReportBpolys(BaseReport, BaseBpolys):
    pass


class ReportDatabase(BaseReport, BaseDatabase):
    pass


INDICATOR_EXAMPLES = {
    "OQT AOI": {
        "summary": (
            "Request an Indicator for an AOI defined by OQT (`dataset` and "
            "`featureId`)."
        ),
        "value": {
            "topic": "building-count",
            "dataset": "regions",
            "featureId": 3,
            "fidField": "ogc_fid",
            "includeSvg": False,
            "includeHtml": False,
            "flatten": False,
        },
    },
    "Custom AOI": {
        "summary": "Request an Indicator for a custom AOI (`bpolys`).",
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
    "Custom AOI and custom Topic": {
        "summary": (
            "Request an Indicator for a custom AOI (`bpolys`) and a custom Topic "
            "(`topic`)."
        ),
        "value": {
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
            "topic": {
                "key": "my-topic-key",
                "name": "My topic name",
                "description": "My topic description",
                "data": {
                    "result": [
                        {"timestamp": "2014-01-01T00:00:00Z", "value": 4708},
                        {"timestamp": "2014-02-01T00:00:00Z", "value": 4842},
                        {"timestamp": "2014-03-01T00:00:00Z", "value": 4840},
                        {"timestamp": "2014-04-01T00:00:00Z", "value": 4941},
                        {"timestamp": "2014-05-01T00:00:00Z", "value": 4987},
                        {"timestamp": "2014-06-01T00:00:00Z", "value": 5007},
                        {"timestamp": "2014-07-01T00:00:00Z", "value": 5020},
                        {"timestamp": "2014-08-01T00:00:00Z", "value": 5168},
                        {"timestamp": "2014-09-01T00:00:00Z", "value": 5355},
                        {"timestamp": "2014-10-01T00:00:00Z", "value": 5394},
                        {"timestamp": "2014-11-01T00:00:00Z", "value": 5449},
                        {"timestamp": "2014-12-01T00:00:00Z", "value": 5470},
                        {"timestamp": "2015-01-01T00:00:00Z", "value": 5475},
                        {"timestamp": "2015-02-01T00:00:00Z", "value": 5477},
                        {"timestamp": "2015-03-01T00:00:00Z", "value": 5481},
                        {"timestamp": "2015-04-01T00:00:00Z", "value": 5495},
                        {"timestamp": "2015-05-01T00:00:00Z", "value": 5516},
                        {"timestamp": "2015-06-01T00:00:00Z", "value": 5517},
                        {"timestamp": "2015-07-01T00:00:00Z", "value": 5519},
                        {"timestamp": "2015-08-01T00:00:00Z", "value": 5525},
                        {"timestamp": "2015-09-01T00:00:00Z", "value": 5560},
                        {"timestamp": "2015-10-01T00:00:00Z", "value": 5564},
                        {"timestamp": "2015-11-01T00:00:00Z", "value": 5568},
                        {"timestamp": "2015-12-01T00:00:00Z", "value": 5627},
                        {"timestamp": "2016-01-01T00:00:00Z", "value": 5643},
                        {"timestamp": "2016-02-01T00:00:00Z", "value": 5680},
                        {"timestamp": "2016-03-01T00:00:00Z", "value": 5681},
                        {"timestamp": "2016-04-01T00:00:00Z", "value": 5828},
                        {"timestamp": "2016-05-01T00:00:00Z", "value": 5974},
                        {"timestamp": "2016-06-01T00:00:00Z", "value": 5990},
                        {"timestamp": "2016-07-01T00:00:00Z", "value": 5991},
                        {"timestamp": "2016-08-01T00:00:00Z", "value": 5997},
                        {"timestamp": "2016-09-01T00:00:00Z", "value": 6002},
                        {"timestamp": "2016-10-01T00:00:00Z", "value": 6010},
                        {"timestamp": "2016-11-01T00:00:00Z", "value": 6010},
                        {"timestamp": "2016-12-01T00:00:00Z", "value": 6016},
                        {"timestamp": "2017-01-01T00:00:00Z", "value": 6015},
                    ]
                },
            },
            "includeSvg": False,
            "includeHtml": False,
            "flatten": False,
        },
    },
}

REPORT_EXAMPLES = {
    "OQT AOI": {
        "summary": (
            "Request a Report for a AOI defined by OQT (`dataset` and `featureId`)."
        ),
        "value": {
            "dataset": "regions",
            "featureId": 12,
            "fidField": "ogc_fid",
            "includeSvg": False,
            "includeHtml": False,
            "flatten": False,
        },
    },
    "Custom AOI": {
        "summary": "Request a Report for a custom AOI (`bpolys`).",
        "value": {
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
            "includeSvg": False,
            "includeHtml": False,
            "flatten": False,
        },
    },
}
