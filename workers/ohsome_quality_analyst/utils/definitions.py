"""Global Variables and Functions."""
import errno
import glob
import logging
import logging.config
import os
import sys
from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, List

import rpy2.rinterface_lib.callbacks
import yaml

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError
from ohsome_quality_analyst.utils.helper import flatten_sequence, get_module_dir

# Dataset names and fid fields which are available in the Geodatabase
DATASETS = MappingProxyType(  # Immutable dict
    {
        "regions": {"default": "ogc_fid", "other": ("name",)},
        "gadm": {
            "default": "uid",  # ISO 3166-1 alpha-3 country code
            "other": (
                *tuple(("name_{0}".format(i) for i in range(6))),
                *tuple(("id_{0}".format(i) for i in range(6))),
                *tuple(("gid_{0}".format(i) for i in range(6))),
            ),
        },
    }
)
# Dataset names and fid fields which are through the API
DATASETS_API = DATASETS.copy()
DATASETS_API.pop("gadm")


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


RASTER_DATASETS = (
    RasterDataset(
        "GHS_BUILT_R2018A",
        "GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.tif",
        "ESRI:54009",
    ),
    RasterDataset(
        "GHS_POP_R2019A",
        "GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif",
        "ESRI:54009",
    ),
    RasterDataset(
        "GHS_SMOD_R2019A",
        "GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif",
        "ESRI:54009",
    ),
    RasterDataset(
        "VNL",
        "VNL_v2_npp_2020_global_vcmslcfg_c202102150000.average_masked.tif",
        "EPSG:4326",
    ),
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
    ("MappingSaturation", "mapaction_major_roads_length"),
    ("MappingSaturation", "mapaction_rail_length"),
    ("MappingSaturation", "mapaction_lakes_area"),
    ("MappingSaturation", "mapaction_rivers_length"),
    ("MappingSaturation", "ideal_vgi_infrastructure"),
    ("MappingSaturation", "ideal_vgi_poi"),
    ("MappingSaturation", "lulc"),
    ("Currentness", "major_roads_count"),
    ("Currentness", "building_count"),
    ("Currentness", "amenities"),
    ("Currentness", "jrc_health_count"),
    ("Currentness", "jrc_education_count"),
    ("Currentness", "jrc_road_count"),
    ("Currentness", "jrc_railway_count"),
    ("Currentness", "jrc_airport_count"),
    ("Currentness", "jrc_water_treatment_plant_count"),
    ("Currentness", "jrc_power_generation_plant_count"),
    ("Currentness", "jrc_cultural_heritage_site_count"),
    ("Currentness", "jrc_bridge_count"),
    ("Currentness", "jrc_mass_gathering_sites_count"),
    ("Currentness", "mapaction_settlements_count"),
    ("Currentness", "mapaction_major_roads_length"),
    ("Currentness", "mapaction_rail_length"),
    ("Currentness", "mapaction_lakes_count"),
    ("Currentness", "mapaction_rivers_length"),
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
# Input geometry size limit in sqkm for API requests
# TODO: decide on default value
GEOM_SIZE_LIMIT = os.getenv("OQT_GEOM_SIZE_LIMIT", default=100)

USER_AGENT = os.getenv(
    "OQT_USER_AGENT",
    default="ohsome-quality-analyst/{0}".format(oqt_version),
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


def get_log_level():
    if "pydevd" in sys.modules or "pdb" in sys.modules:
        default_level = "DEBUG"
    else:
        default_level = "INFO"
    return os.getenv("OQT_LOG_LEVEL", default=default_level)


def load_logging_config():
    """Read logging config from configuration file."""
    level = get_log_level()
    logging_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logging.yaml"
    )
    with open(logging_path, "r") as f:
        logging_config = yaml.safe_load(f)
    logging_config["root"]["level"] = getattr(logging, level.upper())
    return logging_config


def configure_logging() -> None:
    """Configure logging level and format."""

    class RPY2LoggingFilter(logging.Filter):  # Sensitive
        def filter(self, record):
            return " library ‘/usr/share/R/library’ contains no packages" in record.msg

    # Avoid R library contains no packages WARNING logs.
    # OQT has no dependencies on additional R libraries.
    rpy2.rinterface_lib.callbacks.logger.addFilter(RPY2LoggingFilter())
    # Avoid a huge amount of DEBUG logs from matplotlib font_manager.py
    logging.getLogger("matplotlib.font_manager").setLevel(logging.INFO)
    logging.config.dictConfig(load_logging_config())


def load_metadata(module_name: str) -> Dict:
    """Read metadata of all indicators or reports from YAML files.

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
        A Dict with the layer names of the layers as keys.
    """
    directory = get_module_dir("ohsome_quality_analyst.ohsome")
    file = os.path.join(directory, "layer_definitions.yaml")
    with open(file, "r") as f:
        return yaml.safe_load(f)


def get_layer_definition(layer_name: str) -> Dict:
    """Get ohsome API parameters of a single layer based on layer name.

    This is implemented outside the layer class to
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


def get_layer_names() -> List[str]:
    return list(load_layer_definitions().keys())


def get_dataset_names() -> List[str]:
    return list(DATASETS.keys())


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
    return flatten_sequence(DATASETS)


def get_dataset_names_api() -> List[str]:
    return list(DATASETS_API.keys())


def get_fid_fields_api() -> List[str]:
    return flatten_sequence(DATASETS_API)


def get_data_dir() -> str:
    """Get the OQT data directory path."""
    default_dir = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__),
        ),
        "..",
        "..",
        "..",
        "data",
    )
    data_dir = os.getenv("OQT_DATA_DIR", default=default_dir)
    if not os.path.exists(data_dir):
        raise FileNotFoundError(
            errno.ENOENT,
            "OQT data directory does not exists.",
            data_dir,
        )
    return data_dir


def get_attribution(data_keys: list) -> str:
    """Return attribution text. Individual attributions are separated by semicolons."""
    assert set(data_keys) <= set(("OSM", "GHSL", "VNL"))
    filtered = dict(filter(lambda d: d[0] in data_keys, ATTRIBUTION_TEXTS.items()))
    return "; ".join([str(v) for v in filtered.values()])
