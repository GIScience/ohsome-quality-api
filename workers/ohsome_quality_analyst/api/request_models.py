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
    layer_name: LayerEnum = pydantic.Field(
        ..., title="Layer Name", example="building_count"
    )
    include_svg: bool = False
    include_html: bool = False

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

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False
        extra = "forbid"


class BaseReport(BaseModel):
    name: ReportEnum = pydantic.Field(..., title="Report Name", example="SimpleReport")
    include_svg: bool = False
    include_html: bool = False

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False
        extra = "forbid"


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


class IndicatorBpolys(BaseIndicator, BaseBpolys):
    pass


class IndicatorDatabase(BaseIndicator, BaseDatabase):
    pass


class ReportBpolys(BaseReport, BaseBpolys):
    pass


class ReportDatabase(BaseReport, BaseDatabase):
    pass


INDICATOR_EXAMPLES = {
    "Custom AOI": {
        "summary": "Request an Indicator for a custom AOI (`bpolys`).",
        "description": (
            "The parameter `bpolys` has to be a valid GeoJSON Feature or "
            "FeatureCollection object. The Geometry of those objects has to be Polygon "
            "or MultiPolygon. "
        ),
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
    "OQT AOI": {
        "summary": (
            "Request an Indicator for an AOI defined by OQT (`dataset` and "
            "`featureId`)."
        ),
        "description": (
            "Specify `dataset` and `featureId` to request an already calculated "
            "Indicator for an AOI defined by OQT."
        ),
        "value": {
            "name": "GhsPopComparisonBuildings",
            "layerName": "building_count",
            "dataset": "regions",
            "featureId": 3,
        },
    },
}

REPORT_EXAMPLES = {
    "Custom AOI": {
        "summary": "Request a Report for a custom AOI (`bpolys`).",
        "description": (
            "The parameter `bpolys` has to be a valid GeoJSON Feature or "
            "FeatureCollection object. The Geometry of those objects has to be Polygon "
            "or MultiPolygon. "
        ),
        "value": {
            "name": "SimpleReport",
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
    "OQT AOI": {
        "summary": (
            "Request a Report for a AOI defined by OQT (`dataset` and `featureId`)."
        ),
        "description": (
            "Specify `dataset` and `featureId` to request an already calculated "
            "Report for an AOI defined by OQT."
        ),
        "value": {
            "name": "SimpleReport",
            "dataset": "regions",
            "featureId": 3,
        },
    },
}
