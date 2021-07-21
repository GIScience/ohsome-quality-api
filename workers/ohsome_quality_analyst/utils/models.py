"""
Data models of the API request body.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from ohsome_quality_analyst.utils.definitions import (
    get_dataset_names,
    get_fid_fields,
    get_indicator_names,
    get_layer_names,
    get_report_names,
)

IndicatorEnum = Enum("IndicatorNames", {name: name for name in get_indicator_names()})
ReportEnum = Enum("ReportNames", {name: name for name in get_report_names()})
LayerEnum = Enum("LayerNames", {name: name for name in get_layer_names()})
DatasetEnum = Enum("DatasetNames", {name: name for name in get_dataset_names()})
FidFieldEnum = Enum("FidFieldEnum", {name: name for name in get_fid_fields()})


class RequestModel(BaseModel):
    bpolys: Optional[str] = Field(
        None,
        title="Bounding Polygons",
        description=(
            "A GeoJSON Geometry, Feature or FeatureCollection. "
            + "Geometry type must be Ploygon or MultiPolygon."
        ),
        example=str(
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
    )
    dataset: Optional[DatasetEnum] = Field(None, title="Dataset", example="regions")
    featureId: Optional[str] = Field(None, title="Feature Id", example="2")
    fidField: Optional[FidFieldEnum] = Field(
        None, title="Feature Id Field", example="ogc_fid"
    )


class IndicatorModel(RequestModel):
    layerName: LayerEnum = Field(..., title="Layer Name", example="building_count")


class ReportModel(RequestModel):
    pass
