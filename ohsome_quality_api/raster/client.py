"""A client to raster datasets existing as files on disk."""
import logging
import os

from geojson_pydantic import Feature, FeatureCollection
from pyproj import Transformer
from rasterstats import zonal_stats

from ohsome_quality_api.api.request_models import FeatureWithOptionalProperties
from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.raster.definitions import RasterDataset
from ohsome_quality_api.utils.exceptions import RasterDatasetNotFoundError


def get_zonal_stats(
    feature: Feature,
    raster: RasterDataset,
    *args,
    **kwargs,
):
    """Wrapper around the function `zonal_stats` of the package `rasterstats`.

    All arguments are passed directly to `zonal_stats`.

    The only difference is that the arguments `vectors` and `raster` of `zonal_stats`
    are expected to be a `geojson.Feature` object and a member of the `RasterDataset`
    class respectively.
    """
    return zonal_stats(
        transform(feature, raster),
        get_raster_path(raster),
        *args,
        nodata=raster.nodata,
        **kwargs,
    )


def transform(feature: Feature, raster: RasterDataset):
    """Convert Feature to RasterDataset CRS.

    GeoJSON Feature CRS/SRID is expected to be EPSG:4326.
    """
    if raster.crs == "EPSG:4326":
        return feature
    transformer = Transformer.from_crs("EPSG:4326", raster.crs, always_xy=True)

    gjson = reproject_feature_and_feature_collection(
        lambda coordinates: transformer.transform(coordinates[0], coordinates[1]),
        feature.model_dump(),
    )

    if gjson["type"] == "Feature":
        return FeatureWithOptionalProperties(**gjson)
    else:
        return FeatureCollection[FeatureWithOptionalProperties](**gjson)


def get_raster_path(raster: RasterDataset) -> str:
    """Get the path of the raster file on disk."""
    path = os.path.join(get_config_value("data_dir"), raster.filename)
    if not os.path.exists(path):
        raise RasterDatasetNotFoundError(raster)
    return path


def reproject_simple_types(func, obj):
    """Reproject (Multi)-Polygons to new CRS with passable func."""
    if obj["type"] == "Polygon":
        coordinates = [[tuple(func(c)) for c in curve] for curve in obj["coordinates"]]
    elif obj["type"] == "MultiPolygon":
        coordinates = [
            [[tuple(func(c)) for c in curve] for curve in part]
            for part in obj["coordinates"]
        ]
    else:
        logging.debug("Non Polygon Type detected")
    return {"type": obj["type"], "coordinates": coordinates}


def reproject_feature_and_feature_collection(func, obj):
    """Reproject Feature(Collection)s to new CRS with passable func."""
    if obj["type"] == "Feature":
        obj["geometry"] = (
            reproject_simple_types(func, obj["geometry"]) if obj["geometry"] else None
        )
        return obj
    elif obj["type"] == "FeatureCollection":
        feats = [
            reproject_feature_and_feature_collection(func, feat)
            for feat in obj["features"]
        ]
        return {"type": obj["type"], "features": feats}
