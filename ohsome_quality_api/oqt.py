"""Controller for computing Indicators."""

import logging
from typing import Coroutine, List

from geojson import Feature, FeatureCollection

from ohsome_quality_api.indicators.base import BaseIndicator as Indicator
from ohsome_quality_api.topics.models import BaseTopic as Topic
from ohsome_quality_api.topics.models import TopicData, TopicDefinition
from ohsome_quality_api.utils.helper import get_class_from_key
from ohsome_quality_api.utils.helper_asyncio import gather_with_semaphore
from ohsome_quality_api.utils.validators import validate_area


async def create_indicator(
    key: str,
    bpolys: FeatureCollection,
    topic: TopicData | TopicDefinition,
    include_figure: bool = True,
    attribute_keys: List[str] = None,
) -> list[Indicator]:
    """Create indicator(s) for features of a GeoJSON FeatureCollection.

    Indicators are computed asynchronously utilizing semaphores.
    Properties of the input GeoJSON are preserved.
    """
    tasks: list[Coroutine] = []
    for i, feature in enumerate(bpolys.features):
        if "id" not in feature.keys():
            feature["id"] = i
        # Only enforce size limit if ohsome API data is not provided
        # Disable size limit for the Mapping Saturation indicator
        if isinstance(topic, TopicDefinition) and key not in [
            "mapping-saturation",
            "currentness",
            "building-comparison",
            "road-comparison",
            "attribute-completeness",
        ]:
            validate_area(feature)
        tasks.append(
            _create_indicator(key, feature, topic, include_figure, attribute_keys)
        )
    return await gather_with_semaphore(tasks)


async def _create_indicator(
    key: str,
    feature: Feature,
    topic: Topic,
    include_figure: bool = True,
    attribute_keys: List[str] = None,
) -> Indicator:
    """Create an indicator from scratch."""

    logging.info("Indicator key:  {0:4}".format(key))
    logging.info("Topic key:     {0:4}".format(topic.key))
    logging.info("Feature id:     {0:4}".format(feature.get("id", "None")))

    indicator_class = get_class_from_key(class_type="indicator", key=key)
    if key == "attribute-completeness":
        indicator = indicator_class(topic, feature, attribute_keys)
    else:
        indicator = indicator_class(topic, feature)

    logging.info("Run preprocessing")
    await indicator.preprocess()
    logging.info("Run calculation")
    indicator.calculate()

    if include_figure:
        logging.info("Run figure creation")
        indicator.create_figure()
    else:
        indicator.result.figure = None

    return indicator
