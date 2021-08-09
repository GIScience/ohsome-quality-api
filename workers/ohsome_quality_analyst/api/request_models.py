"""
Data models of the API request body.

This module uses the library `pydantic` for data validation and
settings management using Python type hinting.

Besides data validation through `pydantic`, `FastAPI` will display additional
information derived from `pydantic` models in the automatic generated API documentation.
"""

from enum import Enum
from json import JSONDecodeError
from typing import Optional

import geojson
import pydantic

from ohsome_quality_analyst.utils.definitions import (
    get_dataset_names,
    get_fid_fields,
    get_indicator_names,
    get_layer_names,
    get_report_names,
)
from ohsome_quality_analyst.utils.helper import snake_to_lower_camel

IndicatorEnum = Enum("IndicatorEnum", {name: name for name in get_report_names()})
ReportEnum = Enum("ReportEnum", {name: name for name in get_indicator_names()})
LayerEnum = Enum("LayerNames", {name: name for name in get_layer_names()})
DatasetEnum = Enum("DatasetNames", {name: name for name in get_dataset_names()})
FidFieldEnum = Enum("FidFieldEnum", {name: name for name in get_fid_fields()})


class BaseRequestModel(pydantic.BaseModel):
    bpolys: Optional[str]
    dataset: Optional[DatasetEnum]
    feature_id: Optional[str]
    fid_field: Optional[FidFieldEnum]

    @pydantic.root_validator(pre=True)
    @classmethod
    def check_bpolys_or_dataset_and_feature_id(cls, values):
        """Make sure there is either bpolys or dataset and feature_id."""
        if (
            "bpolys" in values
            and "dataset" not in values
            and "feature_id" not in values
        ) or ("bpolys" not in values and "dataset" in values and "featureId" in values):
            return values
        else:
            raise ValueError(
                "Request should contain either the parameter `bpolys` "
                "or `dataset` and `feature_id`."
            )

    @pydantic.validator("bpolys")
    @classmethod
    def validate_bpolys(cls, value) -> str:
        """Validate GeoJSON."""
        try:
            geojson.loads(value)
        except JSONDecodeError as error:
            raise ValueError(
                "The provided parameter `bpolys` is not a valid GeoJSON."
            ) from error

    class Config:
        """Pydantic config class."""

        alias_generator = snake_to_lower_camel
        allow_mutation = False
        fields = {
            "bpolys": {
                "title": "Bounding Polygons",
                "description": (
                    "A GeoJSON Geometry, Feature or FeatureCollection. "
                    + "Geometry type must be Ploygon or MultiPolygon."
                ),
                "example": str(
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
                    }
                ),
            },
            "feature_id": {"example": "3"},
        }


class IndicatorRequestModel(BaseRequestModel):
    layerName: LayerEnum = pydantic.Field(  # noqa: N815
        ..., title="Layer Name", example="building_count"
    )


class ReportRequestModel(BaseRequestModel):
    pass
