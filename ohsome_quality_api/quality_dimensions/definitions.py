"""Global Variables and Functions."""

import os
from enum import Enum

import yaml
from fastapi_i18n import _

from ohsome_quality_api.quality_dimensions.models import QualityDimension
from ohsome_quality_api.utils.helper import get_module_dir


def load_quality_dimensions() -> dict[str, QualityDimension]:
    """Read definitions of quality dimensions.

    Returns:
        A dict with all quality dimensions included.
    """
    directory = get_module_dir("ohsome_quality_api.quality_dimensions")
    file = os.path.join(directory, "quality_dimensions.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    quality_dimensions = {}
    for k, v in raw.items():
        quality_dimensions[k] = QualityDimension(**v)
    return quality_dimensions


def get_quality_dimensions() -> dict[str, QualityDimension]:
    return load_quality_dimensions()


def get_quality_dimension(qd_key: str) -> QualityDimension:
    quality_dimensions = get_quality_dimensions()
    try:
        return quality_dimensions[qd_key]
    except KeyError as error:
        raise KeyError(
            _("Invalid quality dimension key. Valid quality dimension keys are: ")
            + str(quality_dimensions.keys())
        ) from error


def get_quality_dimension_keys() -> list[str]:
    return [str(t) for t in load_quality_dimensions().keys()]


QualityDimensionEnum = Enum(
    "QualityDimensionEnum", {key: key for key in get_quality_dimension_keys()}
)
