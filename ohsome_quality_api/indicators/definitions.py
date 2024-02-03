from enum import Enum

from geojson import FeatureCollection

from ohsome_quality_api.definitions import load_metadata
from ohsome_quality_api.indicators.models import IndicatorMetadata
from ohsome_quality_api.projects.definitions import ProjectEnum
from ohsome_quality_api.topics.definitions import load_topic_presets
from ohsome_quality_api.utils.helper import get_class_from_key


def get_indicator_keys() -> list[str]:
    return list(load_metadata("indicators").keys())


def get_indicator_metadata(project: ProjectEnum = None) -> dict[str, IndicatorMetadata]:
    indicators = load_metadata("indicators")
    if project is not None:
        return {k: v for k, v in indicators.items() if project in v.projects}
    else:
        return indicators


def get_valid_indicators(topic_key: str) -> tuple:
    """Get valid Indicator/Topic combination of a Topic."""
    td = load_topic_presets()
    return tuple(td[topic_key].indicators)


async def get_coverage(indicator_key: str, inverse: bool = False) -> FeatureCollection:
    indicator_class = get_class_from_key(class_type="indicator", key=indicator_key)
    features = await indicator_class.coverage(inverse)
    return FeatureCollection(features=features)


IndicatorEnum = Enum("IndicatorEnum", {name: name for name in get_indicator_keys()})
