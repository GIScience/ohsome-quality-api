"""Global Variables and Functions."""

import glob
import logging
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Literal

import yaml

from ohsome_quality_api.indicators.models import IndicatorMetadata
from ohsome_quality_api.topics.definitions import load_topic_presets
from ohsome_quality_api.utils.helper import (
    camel_to_hyphen,
    get_module_dir,
)

ATTRIBUTION_TEXTS = MappingProxyType(
    {
        "OSM": "© OpenStreetMap contributors",
        "GHSL": "© European Union, 1995-2022, Global Human Settlement Topic Data",
        "VNL": "Earth Observation Group Nighttime Light Data",
        "EUBUCCO": "European building stock characteristics in a common and open "
        + "database",
        "Microsoft Buildings": "Microsoft Building Footprints (ODbL)",
    }
)

ATTRIBUTION_URL = (
    "https://github.com/GIScience/ohsome-quality-api/blob/main/COPYRIGHTS.md"
)


# default colors of the Sematic UI CSS Framework
# used by the ohsome dashboard
class Color(Enum):
    RED = "#DB2828"
    ORANGE = "#F2711C"
    YELLOW = "#FBBD08"
    OLIVE = "#B5CC18"
    GREEN = "#21BA45"
    TEAL = "#00B5AD"
    BLUE = "#2185D0"
    VIOLET = "#6435C9"
    PURPLE = "#A333C8"
    PINK = "#E03997"
    BROWN = "#A5673F"
    GREY = "#767676"
    BLACK = "#1B1C1D"


def load_metadata(
    module_name: Literal["indicators", "reports"],
) -> dict[str, IndicatorMetadata]:
    """Read metadata of all indicators or reports from YAML files.

    Those text files are located in the directory of each indicator/report.

    Args:
        module_name: Either indicators or reports.
    Returns:
        A Dict with the class names of the indicators/reports
        as keys and metadata as values.
    """
    assert module_name == "indicators" or module_name == "reports"
    directory = get_module_dir("ohsome_quality_api.{}".format(module_name))
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
    return metadata


def get_metadata(
    module_name: Literal["indicators", "reports"], class_name: str
) -> IndicatorMetadata:
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
    return set(t.project for t in load_topic_presets().values())


def get_attribution(data_keys: list) -> str:
    """Return attribution text. Individual attributions are separated by semicolons."""
    assert set(data_keys) <= {"OSM", "GHSL", "VNL", "EUBUCCO", "Microsoft Buildings"}
    filtered = dict(filter(lambda d: d[0] in data_keys, ATTRIBUTION_TEXTS.items()))
    return "; ".join([str(v) for v in filtered.values()])
