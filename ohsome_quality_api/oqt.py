"""Controller for computing Indicators and Reports."""

import logging
from typing import Coroutine

from geojson import Feature, FeatureCollection

from ohsome_quality_api.api.request_models import (
    ReportRequest,
)
from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.indicators.base import BaseIndicator as Indicator
from ohsome_quality_api.reports.base import BaseReport as Report
from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import BaseTopic as Topic
from ohsome_quality_api.topics.models import TopicData, TopicDefinition
from ohsome_quality_api.utils.helper import get_class_from_key
from ohsome_quality_api.utils.helper_asyncio import gather_with_semaphore
from ohsome_quality_api.utils.validators import validate_area


async def create_indicator(
    key: str,
    bpolys: FeatureCollection,
    topic: TopicData | TopicDefinition,
    attribute: Attribute | None = None,
    include_figure: bool = True,
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
        ]:
            validate_area(feature)
        tasks.append(_create_indicator(key, feature, topic, attribute, include_figure))
    return await gather_with_semaphore(tasks)


async def create_report(parameters: ReportRequest, key: str) -> FeatureCollection:
    """Create report(s) for features of a GeoJSON FeatureCollection."""
    bpolys = parameters.bpolys
    features = []
    for i, feature in enumerate(bpolys.features):
        if "id" not in feature.keys():
            feature["id"] = i
        validate_area(feature)
        # Reports for a FeatureCollection are not created asynchronously (as it is
        # the case with indicators), because indicators of a report are created
        # asynchronously
        report = await _create_report(key, feature)
        features.append(report.as_feature())
    return FeatureCollection(features=features)


async def _create_indicator(
    key: str,
    feature: Feature,
    topic: Topic,
    attribute: Attribute | None = None,
    include_figure: bool = True,
) -> Indicator:
    """Create an indicator from scratch."""

    logging.info("Indicator key:  {0:4}".format(key))
    logging.info("Topic key:     {0:4}".format(topic.key))
    logging.info("Feature id:     {0:4}".format(feature.get("id", "None")))

    indicator_class = get_class_from_key(class_type="indicator", key=key)
    if key == "attribute-completeness":
        indicator = indicator_class(topic, feature, attribute)
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


async def _create_report(key: str, feature: Feature) -> Report:
    """Create a Report.

    Aggregates all indicator results and calculates an overall quality score.

    Indicators for a Report are created asynchronously utilizing semaphores.
    """

    logging.info("Creating Report...")
    logging.info("Report key:  {0:4}".format(key))
    logging.info("Feature id:  {0:4}".format(feature.get("id", "None")))

    report_class = get_class_from_key(class_type="report", key=key)
    report = report_class(feature=feature)

    tasks: list[Coroutine] = []
    for indicator_key, topic_key in report.indicator_topic:
        topic = get_topic_preset(topic_key)
        tasks.append(_create_indicator(indicator_key, feature, topic))

    report.indicators = await gather_with_semaphore(tasks)
    report.combine_indicators()

    return report
