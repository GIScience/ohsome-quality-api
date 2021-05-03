"""
Global Variables and Functions.
"""

import collections
import glob
import logging
import logging.config
import os
import sys
from typing import Dict

import yaml

from ohsome_quality_analyst.utils.helper import get_module_dir

# Dataset names which are available in the Geodatabase
DATASET_NAMES = (
    "gadm",
    "gadm_level_0",
    "gadm_level_1",
    "gadm_level_2",
    "gadm_level_3",
    "gadm_level_4",
    "gadm_level_5",
    "isea3h_world_res_12_hex",
    "isea3h_world_res_6_hex",
    "nuts_rg_01m_2021",
    "nuts_rg_60m_2021",
    "regions",
)
# Possible indicator layer combinations
INDICATOR_LAYER = (
    ("GhsPopComparisonBuildings", "building_count"),
    ("GhsPopComparisonRoads", "jrc_road_length"),
    ("GhsPopComparisonRoads", "major_roads_length"),
    ("MappingSaturation", "building_count"),
    ("MappingSaturation", "major_roads_length"),
    ("MappingSaturation", "amenities"),
    ("MappingSaturation", "jrc_health_count"),
    ("MappingSaturation", "jrc_mass_gathering_sites_count"),
    ("MappingSaturation", "jrc_railway_length"),
    ("MappingSaturation", "jrc_road_length"),
    ("MappingSaturation", "jrc_education_count"),
    ("MappingSaturation", "mapaction_settlements_count"),
    ("MappingSaturation", "mapaction_capital_city_count"),
    ("MappingSaturation", "major_roads_length"),
    ("LastEdit", "major_roads_count"),
    ("LastEdit", "building_count"),
    ("LastEdit", "amenities"),
    ("LastEdit", "jrc_health_count"),
    ("LastEdit", "jrc_education_count"),
    ("LastEdit", "jrc_road_count"),
    ("LastEdit", "jrc_railway_count"),
    ("LastEdit", "jrc_airport_count"),
    ("LastEdit", "jrc_water_treatment_plant_count"),
    ("LastEdit", "jrc_power_generation_plant_count"),
    ("LastEdit", "jrc_cultural_heritage_site_count"),
    ("LastEdit", "jrc_bridge_count"),
    ("LastEdit", "jrc_mass_gathering_sites_count"),
    ("LastEdit", "mapaction_settlements_count"),
    ("LastEdit", "mapaction_capital_city_count"),
    ("LastEdit", "mapaction_lakes_count"),
    ("LastEdit", "mapaction_rivers_length"),
    ("LastEdit", "mapaction_rail_length"),
    ("PoiDensity", "poi"),
    ("TagsRatio", "jrc_health_count"),
    ("TagsRatio", "jrc_education_count"),
    ("TagsRatio", "jrc_road_length"),
    ("TagsRatio", "jrc_airport_count"),
    ("TagsRatio", "jrc_power_generation_plant_count"),
    ("TagsRatio", "jrc_cultural_heritage_site_count"),
    ("TagsRatio", "jrc_bridge_count"),
    ("TagsRatio", "jrc_mass_gathering_sites_count"),
)
OHSOME_API = os.getenv("OHSOME_API", default="https://api.ohsome.org/v1/")
OHSOME_HEX_API = os.getenv(
    "OHSOME_HEX_API",
    default="https://ohsome.org/apps/osm-history-explorer/ohsomehex-api/",
)
# Input geometry size limit in sqkm for API requests
# TODO: decide on default value
GEOM_SIZE_LIMIT = os.getenv("OQT_GEOM_SIZE_LIMIT", default=100)


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
