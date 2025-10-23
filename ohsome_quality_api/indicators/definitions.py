import os
from enum import Enum

import yaml
from fastapi_i18n import _
from geojson import FeatureCollection

from ohsome_quality_api.indicators.models import IndicatorMetadata
from ohsome_quality_api.projects.definitions import ProjectEnum
from ohsome_quality_api.topics.definitions import load_topic_presets
from ohsome_quality_api.utils.helper import (
    get_class_from_key,
    get_module_dir,
)


def get_indicator_keys() -> list[str]:
    return [str(t) for t in load_indicators().keys()]


def load_indicators() -> dict[str, IndicatorMetadata]:
    directory = get_module_dir("ohsome_quality_api.indicators")
    file = os.path.join(directory, "indicators.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    indicators = {}
    for k, v in raw.items():
        indicators[k] = IndicatorMetadata(**v)
    return indicators


def get_indicator_metadata(project: ProjectEnum = None) -> dict[str, IndicatorMetadata]:
    indicators = load_indicators()
    if project is not None:
        return {k: v for k, v in indicators.items() if project in v.projects}
    else:
        return indicators


def get_indicator(indicator_key: str) -> IndicatorMetadata:
    indicators = get_indicator_metadata()
    try:
        return indicators[indicator_key]
    except KeyError as error:
        raise KeyError(
            _("Invalid project key. Valid project keys are: ") + str(indicators.keys())
        ) from error


def get_valid_indicators(topic_key: str) -> tuple:
    """Get valid Indicator/Topic combination of a Topic."""
    td = load_topic_presets()
    return tuple(td[topic_key].indicators)


async def get_coverage(indicator_key: str, inverse: bool = False) -> FeatureCollection:
    indicator_class = get_class_from_key(class_type="indicator", key=indicator_key)
    features = await indicator_class.coverage(inverse)
    return FeatureCollection(features=features)


IndicatorEnum = Enum("IndicatorEnum", {name: name for name in get_indicator_keys()})
IndicatorEnumRequest = Enum(
    "IndicatorEnum",
    {name: name for name in get_indicator_keys() if name != "attribute-completeness"},
)
