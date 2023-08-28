"""A client to raster datasets existing as files on disk."""

import os
from copy import deepcopy

import geojson
from pyproj import Transformer
from rasterstats import zonal_stats

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.raster.definitions import RasterDataset
from ohsome_quality_api.utils.exceptions import RasterDatasetNotFoundError


def get_zonal_stats(
    feature: geojson.Feature,
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


def transform(feature: geojson.Feature, raster: RasterDataset):
    """Convert Feature to RasterDataset CRS.

    GeoJSON Feature CRS/SRID is expected to be EPSG:4326.
    """
    if raster.crs == "EPSG:4326":
        return feature
    transformer = Transformer.from_crs("EPSG:4326", raster.crs, always_xy=True)
    return geojson.utils.map_tuples(
        lambda coordinates: transformer.transform(coordinates[0], coordinates[1]),
        deepcopy(feature),
    )


def get_raster_path(raster: RasterDataset) -> str:
    """Get the path of the raster file on disk."""
    path = os.path.join(get_config_value("data_dir"), raster.filename)
    if not os.path.exists(path):
        raise RasterDatasetNotFoundError(raster)
    return path
