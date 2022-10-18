"""Global Variables and Functions."""
from __future__ import annotations

import glob
import logging
import os
from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, List, Literal, Optional

import yaml

from ohsome_quality_analyst.base.layer import LayerDefinition
from ohsome_quality_analyst.config import get_config_value
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError
from ohsome_quality_analyst.utils.helper import flatten_sequence, get_module_dir


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
    nodata: Optional[int]


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
        "GHSL": "© European Union, 1995-2022, Global Human Settlement Layer Data",
        "VNL": "Earth Observation Group Nighttime Light Data",
    }
)

ATTRIBUTION_URL = (
    "https://github.com/GIScience/ohsome-quality-analyst/blob/main/data/"
    + "COPYRIGHTS.md"
)


def load_metadata(module_name: Literal["indicators", "reports"]) -> Dict:
    """Load metadata of all indicators or reports from YAML files.

    The YAML files are located in the directory of each individual indicator or report.

    Returns:
        A dictionary with the indicator or report keys as directory keys and the content
        of the YAML file (metadata) as values.
    """
    # TODO: Is this check needed if Literal is used in func declaration?
    if module_name != "indicators" and module_name != "reports":
        raise ValueError("module name value can only be 'indicators' or 'reports'.")

    directory = get_module_dir("ohsome_quality_analyst.{0}".format(module_name))
    files = glob.glob(directory + "/**/metadata.yaml", recursive=True)
    metadata = {}
    for file in files:
        with open(file, "r") as f:
            metadata = {**metadata, **yaml.safe_load(f)}  # Merge dicts
    return metadata


def get_metadata(module_name: str, class_name: str) -> Dict:
    """Get metadata of an indicator or report based on its class name.

    This is implemented outside the metadata class to be able to
    access metadata of all indicators/reports without instantiation of those.

    Args:
        module_name: Either indicators or reports.
        class_name: Any class name in Camel Case which is implemented
                    as report or indicator
    """
    if module_name not in ("indicators", "reports"):
        raise ValueError("module name value can only be 'indicators' or 'reports'.")

    metadata = load_metadata(module_name)
    try:
        return metadata[class_name]
    except KeyError:
        logging.error(
            "Invalid {0} class name. Valid {0} class names are: ".format(
                module_name[:-1]
            )
            + str(metadata.keys())
        )
        raise


def load_layer_definitions() -> Dict:
    """Read ohsome API parameters of all layer from YAML file.

    Returns:
        A dict with all layers included.
    """
    directory = get_module_dir("ohsome_quality_analyst.ohsome")
    file = os.path.join(directory, "layer_definitions.yaml")
    with open(file, "r") as f:
        return yaml.safe_load(f)


def get_layer_definition(layer_key: str) -> LayerDefinition:
    """Get ohsome API parameters of a single layer based on layer key.

    This is implemented outside the layer class to
    be able to access layer definitions of all indicators without
    instantiation of those.
    """
    layers = load_layer_definitions()
    try:
        layer = layers[layer_key]
    except KeyError as error:
        raise KeyError(
            "Invalid layer key. Valid layer keys are: " + str(layers.keys())
        ) from error
    # Avoid built-in function name `filter`
    layer["filter_"] = layer.pop("filter")
    layer["key"] = layer_key
    return LayerDefinition(**layer)


def get_indicator_classes() -> Dict:
    """Map indicator name to corresponding class."""
    raise NotImplementedError(
        "Use utils.definitions.load_indicator_metadata() and"
        + "utils.helper.name_to_class() instead"
    )


def get_report_classes() -> Dict:
    """Map report name to corresponding class."""
    raise NotImplementedError(
        "Use utils.definitions.load_indicator_metadata() and"
        + "utils.helper.name_to_class() instead"
    )


def get_indicator_names() -> List[str]:
    return list(load_metadata("indicators").keys())


def get_report_names() -> List[str]:
    return list(load_metadata("reports").keys())


def get_layer_keys() -> List[str]:
    return list(load_layer_definitions().keys())


def get_dataset_names() -> List[str]:
    return list(get_config_value("datasets").keys())


def get_raster_dataset_names() -> List[str]:
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


def get_fid_fields() -> List[str]:
    return flatten_sequence(get_config_value("datasets").values())


def get_attribution(data_keys: list) -> str:
    """Return attribution text. Individual attributions are separated by semicolons."""
    assert set(data_keys) <= set(("OSM", "GHSL", "VNL"))
    filtered = dict(filter(lambda d: d[0] in data_keys, ATTRIBUTION_TEXTS.items()))
    return "; ".join([str(v) for v in filtered.values()])


def get_valid_layers(indicator_name: str) -> list:
    """Get valid Indicator/Layer combination of an indicator."""
    indicator_layer = load_metadata("indicators")
    valid_layers = []
    for key, value in indicator_layer.items():
        if key == indicator_name:
            for comb in value["layer-thresholds"]:
                valid_layers.append(comb["layer"])
    return [l for l in valid_layers if l is not None]  # noqa: E741


def get_valid_indicators(layer_key: str) -> list:
    """Get valid Indicator/Layer combination of a layer."""
    indicator_layer = load_metadata("indicators")
    valid_indicators = []
    for key, value in indicator_layer.items():
        if any(comb["layer"] == layer_key for comb in value["layer-thresholds"]):
            valid_indicators.append(key)
    return valid_indicators
