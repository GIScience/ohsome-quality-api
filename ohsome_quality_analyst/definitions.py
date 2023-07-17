"""Global Variables and Functions."""
import glob
import logging
from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Literal

import yaml

from ohsome_quality_analyst.config import get_config_value
from ohsome_quality_analyst.indicators.models import IndicatorMetadata
from ohsome_quality_analyst.reports.models import ReportMetadata
from ohsome_quality_analyst.topics.definitions import load_topic_definitions
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError
from ohsome_quality_analyst.utils.helper import (
    camel_to_hyphen,
    flatten_sequence,
    get_module_dir,
)


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

ATTRIBUTION_TEXTS = MappingProxyType(
    {
        "OSM": "© OpenStreetMap contributors",
        "GHSL": "© European Union, 1995-2022, Global Human Settlement Topic Data",
        "VNL": "Earth Observation Group Nighttime Light Data",
    }
)

ATTRIBUTION_URL = (
    "https://github.com/GIScience/ohsome-quality-analyst/blob/main/COPYRIGHTS.md"
)


def load_metadata(
    module_name: Literal["indicators", "reports"]
) -> dict[str, IndicatorMetadata | ReportMetadata]:
    """Read metadata of all indicators or reports from YAML files.

    Those text files are located in the directory of each indicator/report.

    Args:
        module_name: Either indicators or reports.
    Returns:
        A Dict with the class names of the indicators/reports
        as keys and metadata as values.
    """
    assert module_name == "indicators" or module_name == "reports"
    directory = get_module_dir("ohsome_quality_analyst.{}".format(module_name))
    files = glob.glob(directory + "/**/metadata.yaml", recursive=True)
    raw = {}
    for file in files:
        with open(file, "r") as f:
            raw.update(yaml.safe_load(f))  # Merge dicts
    metadata = {}
    match module_name:
        case "indicators":
            for k, v in raw.items():
                metadata[k] = IndicatorMetadata(**v)
        case "reports":
            for k, v in raw.items():
                metadata[k] = ReportMetadata(**v)
    return metadata


def get_metadata(
    module_name: Literal["indicators", "reports"], class_name: str
) -> IndicatorMetadata | ReportMetadata:
    """Get metadata of an indicator or report based on its class name.

    This is implemented outside the metadata class to be able to access metadata of all
    indicators/reports without instantiating of those.

    Args:
        module_name: Either indicators or reports.
        class_name: Class name of an indicator (camel case).
    """
    metadata = load_metadata(module_name)
    try:
        return metadata[camel_to_hyphen(class_name)]
    except KeyError:
        logging.error("Invalid class name: " + class_name)
        raise


# TODO: duplicate of func with the same name in projects/definition.py ?
def get_project_keys() -> Iterable[str]:
    return set(t.project for t in load_topic_definitions().values())


def get_dataset_names() -> list[str]:
    return list(get_config_value("datasets").keys())


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


def get_fid_fields() -> list[str]:
    return flatten_sequence(get_config_value("datasets").values())


def get_attribution(data_keys: list) -> str:
    """Return attribution text. Individual attributions are separated by semicolons."""
    assert set(data_keys) <= {"OSM", "GHSL", "VNL"}
    filtered = dict(filter(lambda d: d[0] in data_keys, ATTRIBUTION_TEXTS.items()))
    return "; ".join([str(v) for v in filtered.values()])
