"""
Global Variables and Functions.
"""

import collections
import glob
import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Dict

import yaml
from xdg import XDG_DATA_HOME

from ohsome_quality_analyst.utils.helper import get_module_dir

# Dataset names which are available in the Geodatabase
DATASET_NAMES = (
    "nuts_rg_60m_2021",
    "nuts_rg_01m_2021",
    "isea3h_world_res_6_hex",
    "isea3h_world_res_12_hex",
    "gadm",
    "gadm_level_0",
    "gadm_level_1",
    "gadm_level_2",
    "gadm_level_3",
    "gadm_level_4",
    "gadm_level_5",
    "test_data",
    "test_regions",
)
# Possible indicator layer combinations
INDICATOR_LAYER = (
    ("GhsPopComparison", "building_count"),
    ("MappingSaturation", "building_count"),
    ("MappingSaturation", "major_roads"),
    ("MappingSaturation", "amenities"),
    ("LastEdit", "major_roads"),
    ("LastEdit", "building_count"),
    ("LastEdit", "amenities"),
    ("PoiDensity", "poi"),
)
OHSOME_API = os.getenv("OHSOME_API", default="https://api.ohsome.org/v1/")
DATA_HOME_PATH = os.path.join(XDG_DATA_HOME, "ohsome_quality_analyst")
DATA_PATH = os.path.join(DATA_HOME_PATH, "data")
Path(DATA_HOME_PATH).mkdir(parents=True, exist_ok=True)
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)


def get_log_level():
    if "pydevd" in sys.modules or "pdb" in sys.modules:
        default_level = "DEBUG"
    else:
        default_level = "INFO"
    return os.getenv("OQT_LOG_LEVEL", default=default_level)


def load_logging_config():
    """Read logging config from configuration file"""
    level = get_log_level()
    logging_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logging.yaml"
    )
    with open(logging_path, "r") as f:
        logging_config = yaml.safe_load(f)
    logging_config["root"]["level"] = getattr(logging, level.upper())
    return logging_config


def configure_logging() -> None:
    """Configure logging level and format"""
    logging.config.dictConfig(load_logging_config())


def load_metadata(module_name: str) -> Dict:
    """
    Read metadata of all indicators or reports from YAML files.

    Those text files are located in the directory of each indicator/report.

    Args:
        module_name: Either indicators or reports.
    Returns:
        A Dict with the class names of the indicators/reports
        as keys and metadata as values.
    """
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

    This is implemented outsite of the metadata class to be able to
    access metadata of all indicators/reports without instantiation of those.

    Args:
        module_name: Either indicators or reports.
        class_name: Any class name in Camel Case which is implemented
                    as report or indicator
    """
    if module_name != "indicators" and module_name != "reports":
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
    """
    Read ohsome API parameters of all layer from YAML file.

    Returns:
        A Dict with the layer names of the layers as keys.
    """
    directory = get_module_dir("ohsome_quality_analyst.ohsome")
    file = os.path.join(directory, "layer_definitions.yaml")
    with open(file, "r") as f:
        return yaml.safe_load(f)


def get_layer_definition(layer_name: str) -> Dict:
    """
    Get ohsome API parameters of a single layer based on layer name.

    This is implemented outsite of the layer class to
    be able to access layer definitions of all indicators without
    instantiation of those.
    """
    layers = load_layer_definitions()
    try:
        return layers[layer_name]
    except KeyError:
        logging.error(
            "Invalid layer name. Valid layer names are: " + str(layers.keys())
        )
        raise


def get_indicator_classes() -> Dict:
    """Map indicator name to corresponding class"""
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


ReportResult = collections.namedtuple("Result", "label value text")
ReportMetadata = collections.namedtuple("Metadata", "name description")
