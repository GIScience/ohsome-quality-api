"""Data models of the API request body.

This module uses the library `pydantic` for data validation and
settings management using Python type hinting.

Besides data validation through `pydantic`, `FastAPI` will display additional
information derived from `pydantic` models in the automatic generated API documentation.
"""

from enum import Enum
from typing import Optional, Union

import pydantic
from geojson import Feature, FeatureCollection
from pydantic import BaseModel

from ohsome_quality_analyst.base.layer import LayerData
from ohsome_quality_analyst.utils.definitions import (
    INDICATOR_LAYER,
    get_dataset_names_api,
    get_fid_fields_api,
    get_indicator_names,
    get_layer_names,
    get_report_names,
)
from ohsome_quality_analyst.utils.helper import loads_geojson, snake_to_lower_camel

IndicatorEnum = Enum("IndicatorEnum", {name: name for name in get_indicator_names()})
ReportEnum = Enum("ReportEnum", {name: name for name in get_report_names()})
LayerEnum = Enum("LayerNames", {name: name for name in get_layer_names()})
DatasetEnum = Enum("DatasetNames", {name: name for name in get_dataset_names_api()})
FidFieldEnum = Enum("FidFieldEnum", {name: name for name in get_fid_fields_api()})


class BaseIndicator(BaseModel):
    name: IndicatorEnum = pydantic.Field(
        ..., title="Indicator Name", example="GhsPopComparisonBuildings"
    )
    include_svg: bool = False
    include_html: bool = False
    include_data: bool = False
    flatten: bool = True

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False
        extra = "forbid"


class BaseReport(BaseModel):
    name: ReportEnum = pydantic.Field(
        ..., title="Report Name", example="MinimalTestReport"
    )
    include_svg: bool = False
    include_html: bool = False
    include_data: bool = False
    flatten: bool = True

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False
        extra = "forbid"


class BaseLayerName(BaseModel):
    """Model for the `layer_name` parameter."""

    layer_name: LayerEnum = pydantic.Field(
        ..., title="Layer Name", example="building_count"
    )


class BaseLayerData(BaseModel):
    """Model for the parameter `layer`.

    The Layer consists of name, description and data.
    """

    layer: LayerData


class BaseBpolys(BaseModel):
    """Model for the `bpolys` parameter."""

    bpolys: Union[Feature, FeatureCollection] = pydantic.Field(
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
    def validate_bpolys(cls, value) -> dict:
        """Validate GeoJSON."""
        # Load and validate GeoJSON
        for _ in loads_geojson(value):
            # Check if exceptions are raised by `loads_geojson`
            pass
        return value


class BaseDatabase(BaseModel):
    """Model for the combination of parameters: `dataset`, `feature_id`, `fid_field`."""

    dataset: DatasetEnum = pydantic.Field(..., title="Dataset Name", example="regions")
    feature_id: str = pydantic.Field(..., title="Feature Id", example="3")
    fid_field: Optional[FidFieldEnum] = None


class IndicatorBpolys(BaseIndicator, BaseLayerName, BaseBpolys):
    @pydantic.root_validator
    @classmethod
    def validate_indicator_layer(cls, values):
        try:
            indicator_layer = (values["name"].value, values["layer_name"].value)
        except KeyError:
            raise ValueError("An issue with the layer or indicator name occurred.")
        if indicator_layer not in INDICATOR_LAYER:
            raise ValueError(
                "Indicator layer combination is invalid: " + str(indicator_layer)
            )
        else:
            return values


class IndicatorDatabase(BaseIndicator, BaseLayerName, BaseDatabase):
    @pydantic.root_validator
    @classmethod
    def validate_indicator_layer(cls, values):
        try:
            indicator_layer = (values["name"].value, values["layer_name"].value)
        except KeyError:
            raise ValueError("An issue with the layer or indicator name occurred.")
        if indicator_layer not in INDICATOR_LAYER:
            raise ValueError(
                "Indicator layer combination is invalid: " + str(indicator_layer)
            )
        else:
            return values


class IndicatorData(BaseIndicator, BaseLayerData, BaseBpolys):
    @pydantic.validator("name")
    @classmethod
    def validate_indicator_name(cls, name):
        if name.value != "MappingSaturation":
            raise ValueError(
                "Computing an Indicator for a Layer with data attached is only "
                + "supported for the Mapping Saturation Indicator."
            )
        else:
            return name


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
            "name": "GhsPopComparisonBuildings",
            "layerName": "building_count",
            "dataset": "regions",
            "featureId": 3,
            "fidField": "ogc_fid",
            "includeSvg": False,
            "includeHtml": False,
            "flatten": True,
        },
    },
    "Custom AOI": {
        "summary": "Request an Indicator for a custom AOI (`bpolys`).",
        "value": {
            "name": "GhsPopComparisonBuildings",
            "layerName": "building_count",
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
    "Custom AOI and custom Layer": {
        "summary": (
            "Request an Indicator for a custom AOI (`bpolys`) and a custom Layer "
            "(`layer`)."
        ),
        "value": {
            "name": "MappingSaturation",
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
            "layer": {
                "name": "My layer name",
                "description": "My layer description",
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
            "flatten": True,
        },
    },
}

REPORT_EXAMPLES = {
    "OQT AOI": {
        "summary": (
            "Request a Report for a AOI defined by OQT (`dataset` and `featureId`)."
        ),
        "value": {
            "name": "MinimalTestReport",
            "dataset": "regions",
            "featureId": 3,
            "fidField": "ogc_fid",
            "includeSvg": False,
            "includeHtml": False,
            "flatten": True,
        },
    },
    "Custom AOI": {
        "summary": "Request a Report for a custom AOI (`bpolys`).",
        "value": {
            "name": "MinimalTestReport",
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
            "flatten": True,
        },
    },
}
