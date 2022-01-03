"""Data models of the API request body.

This module uses the library `pydantic` for data validation and
settings management using Python type hinting.

Besides data validation through `pydantic`, `FastAPI` will display additional
information derived from `pydantic` models in the automatic generated API documentation.
"""

from enum import Enum
from typing import Optional

import pydantic

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


class BaseIndicatorModel(pydantic.BaseModel):
    name: IndicatorEnum = pydantic.Field(
        ..., title="Indicator Name", example="GhsPopComparisonBuildings"
    )
    layer_name: LayerEnum = pydantic.Field(
        ..., title="Layer Name", example="building_count"
    )
    include_svg: bool = False

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


class BaseReportModel(pydantic.BaseModel):
    name: ReportEnum = pydantic.Field(..., title="Report Name", example="SimpleReport")
    include_svg: bool = False

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False


class BaseGETModel(pydantic.BaseModel):
    dataset: DatasetEnum = pydantic.Field(..., title="Dataset Name", example="regions")
    feature_id: str = pydantic.Field(..., title="Feature Id", example="3")
    fid_field: Optional[FidFieldEnum]


class BasePOSTModel(pydantic.BaseModel):
    bpolys: Optional[dict]
    dataset: Optional[DatasetEnum]
    feature_id: Optional[str]
    fid_field: Optional[FidFieldEnum]

    @pydantic.root_validator(pre=True)
    @classmethod
    def check_bpolys_or_dataset_and_feature_id(cls, values):
        """Make sure either bpolys or dataset and feature_id are given as parameters."""
        # featureId is a pydantic alias for feature_id (See config class below)
        _values = list(map(snake_to_lower_camel, values))
        if (
            "bpolys" in _values
            and not any(v in _values for v in ("dataset", "featureId"))
        ) or (
            "bpolys" not in _values
            and all(v in _values for v in ("dataset", "featureId"))
        ):
            return values
        else:
            raise ValueError(
                "Request should contain either the parameter `bpolys` "
                "or `dataset` and `featureId`."
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

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False
        fields = {
            "bpolys": {
                "title": "Bounding Polygons",
                "description": (
                    "A GeoJSON Geometry, Feature or FeatureCollection. "
                    + "Geometry type must be Polygon or MultiPolygon."
                ),
                "example": {
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
            "dataset": {"title": "Dataset Name", "example": "regions"},
            "feature_id": {"title": "Feature Id", "example": "3"},
            "fid_field": {"title": "Feature Id Field", "example": "ogc_fid"},
        }


class IndicatorGETRequestModel(BaseGETModel, BaseIndicatorModel):
    pass


class IndicatorPOSTRequestModel(BasePOSTModel, BaseIndicatorModel):
    pass


class ReportGETRequestModel(BaseGETModel, BaseReportModel):
    pass


class ReportPOSTRequestModel(BasePOSTModel, BaseReportModel):
    pass
