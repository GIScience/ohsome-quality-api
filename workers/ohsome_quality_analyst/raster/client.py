"""A client to raster datasets existing as files on disk."""
import os
from copy import deepcopy
from typing import Union

import geojson
from pyproj import Transformer
from rasterstats import zonal_stats

from ohsome_quality_analyst.utils.definitions import RasterDataset, get_data_dir
from ohsome_quality_analyst.utils.exceptions import (
    RasterDatasetNotFoundError,
    RasterNoData,
)


def get_zonal_stats(
    feature: geojson.Feature,
    raster: RasterDataset,
    stats: Union[list, tuple] = (
        "count",
        "max",
        "mean",
        "min",
    ),  # Default of `rasterstats`
    *args,
    **kwargs,
):
    """Wrapper around the function `zonal_stats` of the package `rasterstats`.

    All arguments are passed directly to `zonal_stats`.

    The only difference is that the arguments `vectors` and `raster` of `zonal_stats`
    are expected to be a `geojson.Feature` object and a member of the `RasterDataset`
    class respectively.

    Raises:
        RasterNoData: If count of pixel is 0 raise exception. NoData values are not
        counted. Pixel count is 0 also if the AOI is outside of the Raster extend.
    """
    results = zonal_stats(
        transform(feature, raster),
        get_raster_path(raster),
        stats=["count", *stats],
        nodata=raster.nodata,
        *args,
        **kwargs,
    )
    # Filter out "count" if not in input stats list
    if all([result["count"] for result in results]):  # Truth value of `0` is `False`
        return [{k: v for k, v in result.items() if k in stats} for result in results]
    else:
        raise RasterNoData(raster.name)


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
    path = os.path.join(get_data_dir(), raster.filename)
    if not os.path.exists(path):
        raise RasterDatasetNotFoundError(raster)
    return path
