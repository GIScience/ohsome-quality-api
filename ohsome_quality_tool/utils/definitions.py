import collections
import glob
import logging.config
import os
import pkgutil
from enum import Enum
from pathlib import Path
from typing import Dict

import yaml
from xdg import XDG_DATA_HOME

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
    "test-regions",
)
OHSOME_API = os.getenv("OHSOME_API", default="https://api.ohsome.org/v1/")
DATA_HOME_PATH = os.path.join(XDG_DATA_HOME, "ohsome_quality_tool")
DATA_PATH = os.path.join(DATA_HOME_PATH, "data")


class TrafficLightQualityLevels(Enum):
    """The Quality Levels"""

    GREEN = 1
    YELLOW = 2
    RED = 3
    UNDEFINED = 4


def get_logger():
    logs_path = os.path.join(DATA_HOME_PATH, "logs")
    logging_file_path = os.path.join(logs_path, "oqt.log")
    logging_config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logging.yaml"
    )
    Path(logs_path).mkdir(parents=True, exist_ok=True)

    with open(logging_config_path, "r") as f:
        logging_config = yaml.safe_load(f)
    logging_config["handlers"]["file"]["filename"] = logging_file_path
    logging.config.dictConfig(logging_config)

    return logging.getLogger("oqt")


def get_module_dir(module_name: str) -> str:
    module = pkgutil.get_loader(module_name)
    return os.path.dirname(module.get_filename())


def load_indicator_metadata() -> Dict:
    """Read metadata of indicators from text files.

    Those text files are located in the directory of each indicator.
    Returns a Dict with class names of the indicatros as keys and metadata as values.
    """
    directory = get_module_dir("ohsome_quality_tool.indicators")
    files = glob.glob(directory + "/**/metadata.yaml", recursive=True)
    metadata = {}
    for file in files:
        with open(file, "r") as f:
            metadata = {**metadata, **yaml.safe_load(f)}  # Merge dicts
    return metadata


def load_layer_definitions() -> Dict:
    """Read ohsome API parameter of each layer from text file."""
    directory = get_module_dir("ohsome_quality_tool.ohsome")
    file = os.path.join(directory, "layer_definitions.yaml")
    with open(file, "r") as f:
        return yaml.safe_load(f)


def get_layer_definition(layer_name: str) -> Dict:
    """Get defintion of an layer based on layer name."""
    layers = load_layer_definitions()
    try:
        return layers[layer_name]
    except KeyError:
        logger.info("Invalid layer name. Valid layer names are: " + str(layers.keys()))
        raise
    pass


def get_indicator_metadata(indicator_name: str) -> Dict:
    """Get metadata of an indicator based on indicator class name."""
    indicators = load_indicator_metadata()
    try:
        return indicators[indicator_name]
    except KeyError:
        logger.info(
            "Invalid indicator name. Valid indicator names are: "
            + str(indicators.keys())
        )
        raise


def get_indicator_classes() -> Dict:
    """Map indicator name to corresponding class"""
    # To avoid circular imports classes are imported only once this function is called.
    from ohsome_quality_tool.indicators.ghs_pop_comparison.indicator import (
        Indicator as ghspopComparisonIndicator,
    )
    from ohsome_quality_tool.indicators.guf_comparison.indicator import (
        GufComparison as gufComparisonIndicator,
    )
    from ohsome_quality_tool.indicators.last_edit.indicator import (
        Indicator as lastEditIndicator,
    )
    from ohsome_quality_tool.indicators.mapping_saturation.indicator import (
        Indicator as mappingSaturationIndicator,
    )
    from ohsome_quality_tool.indicators.poi_density.indicator import (
        Indicator as poiDensityIndicator,
    )

    return {
        "ghspop-comparison": ghspopComparisonIndicator,
        "poi-density": poiDensityIndicator,
        "last-edit": lastEditIndicator,
        "mapping-saturation": mappingSaturationIndicator,
        "guf-comparison": gufComparisonIndicator,
    }


def get_report_classes() -> Dict:
    """Map report name to corresponding class."""
    # To avoid circular imports classes are imported only once this function is called.
    from ohsome_quality_tool.reports.remote_mapping_level_one.report import (
        Report as remoteMappingLevelOneReport,
    )
    from ohsome_quality_tool.reports.simple_report.report import Report as simpleReport
    from ohsome_quality_tool.reports.sketchmap_fitness.report import (
        Report as sketchmapFitnessReport,
    )

    return {
        "sketchmap-fitness": sketchmapFitnessReport,
        "remote-mapping-level-one": remoteMappingLevelOneReport,
        "simple-report": simpleReport,
    }


LayerDefinition = collections.namedtuple(
    "LayerDefinition", "name description filter unit"
)
IndicatorResult = collections.namedtuple("Result", ["label", "value", "text", "svg"])
IndicatorMetadata = collections.namedtuple(
    "Metadata", "name description filterName filterDescription"
)

ReportResult = collections.namedtuple("Result", "label value text")
ReportMetadata = collections.namedtuple("Metadata", "name description")
Path(DATA_HOME_PATH).mkdir(parents=True, exist_ok=True)
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)

logger = get_logger()
