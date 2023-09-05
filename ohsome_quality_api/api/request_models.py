# ruff: noqa: N805
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from geojson_pydantic import (
    Feature as PydanticFeature,
)
from geojson_pydantic import (
    FeatureCollection as PydanticFeatureCollection,
)
from geojson_pydantic import (
    MultiPolygon,
    Polygon,
)
from geojson_pydantic.features import Feat, Geom, Props
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ohsome_quality_api.topics.definitions import TopicEnum
from ohsome_quality_api.topics.models import TopicData
from ohsome_quality_api.utils.exceptions import InvalidCRSError
from ohsome_quality_api.utils.helper import snake_to_lower_camel


class BaseConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake_to_lower_camel,
        populate_by_name=True,
        frozen=True,
        extra="forbid",
    )


class Feature(PydanticFeature[Geom, Props], Generic[Geom, Props]):
    """Extended Feature that make properties optional."""

    properties: Optional[Union[Props, None]] = None


Crs = TypeVar("Crs", bound=Union[Dict[str, Any], BaseModel])


class FeatureCollection(PydanticFeatureCollection[Feat], Generic[Feat]):
    """Extended FeatureCollection that also checks for CRS."""

    crs: Optional[Union[Crs, None]] = None

    @field_validator("crs", mode="before")
    def check_crs(cls, crs: dict):
        """Check if CRS is not WGS84"""
        if crs is None:
            return
        if crs["type"] != "name":
            raise InvalidCRSError(
                "Invalid CRS. CRS object is not according to specification."
            )
        if crs["properties"]["name"] not in [
            "urn\\:ogc:def:crs:OGC:1.3:CRS84",
            "EPSG:4326",
        ]:
            raise InvalidCRSError("Invalid CRS. GeoJSON must be in WGS84 (EPSG:4326).")


class BaseBpolys(BaseConfig):
    bpolys: FeatureCollection[Feature[Polygon | MultiPolygon, Props]]


class IndicatorRequest(BaseBpolys):
    topic_key: TopicEnum = Field(
        ...,
        title="Topic Key",
        alias="topic",
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
