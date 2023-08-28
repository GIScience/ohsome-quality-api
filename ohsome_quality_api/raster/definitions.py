from dataclasses import dataclass

from ohsome_quality_api.utils.exceptions import RasterDatasetUndefinedError


@dataclass(frozen=True)
class RasterDataset:
    """Raster datasets available on disk.

    Args:
        name: Name of raster
        filename: Filename of raster on disk
        crs: An authority string (i.e. `EPSG:4326` or `ESRI:54009`)
    """

    name: str
    filename: str
    crs: str
    nodata: int | None


RASTER_DATASETS = (
    RasterDataset(
        "GHS_BUILT_R2018A",
        "GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.tif",
        "ESRI:54009",
        -200,
    ),
    RasterDataset(
        "GHS_POP_R2019A",
        "GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif",
        "ESRI:54009",
        -200,
    ),
    RasterDataset(
        "GHS_SMOD_R2019A",
        "GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif",
        "ESRI:54009",
        -200,
    ),
    RasterDataset(
        "VNL",
        "VNL_v2_npp_2020_global_vcmslcfg_c202102150000.average_masked.tif",
        "EPSG:4326",
        -999,
    ),
)


def get_raster_dataset_names() -> list[str]:
    return [r.name for r in RASTER_DATASETS]


def get_raster_dataset(name: str) -> RasterDataset:
    """Get a instance of the `RasterDataset` class by the raster name.

    Args:
        name: Name of the raster as defined by `RASTER_DATASETS`.

    Returns
        An instance of the `RasterDataset` class with matching name.

    Raises:
        RasterDatasetUndefinedError: If no matching `RasterDataset` class is found.
    """
    try:
        return next(filter(lambda r: r.name == name, RASTER_DATASETS))
    except StopIteration as e:
        raise RasterDatasetUndefinedError(name) from e
