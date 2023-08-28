"""Controller for computing Indicators and Reports."""

import logging
from typing import Coroutine

from geojson_pydantic import Feature, FeatureCollection

from ohsome_quality_analyst.api.request_models import (
    ReportRequest,
)
from ohsome_quality_analyst.indicators.base import BaseIndicator as Indicator
from ohsome_quality_analyst.reports.base import BaseReport as Report
from ohsome_quality_analyst.topics.definitions import get_topic_preset
from ohsome_quality_analyst.topics.models import BaseTopic as Topic
from ohsome_quality_analyst.topics.models import TopicData, TopicDefinition
from ohsome_quality_analyst.utils.helper import get_class_from_key
from ohsome_quality_analyst.utils.helper_asyncio import gather_with_semaphore
from ohsome_quality_analyst.utils.validators import validate_area


async def create_indicator(
    key: str,
    bpolys: FeatureCollection,
    topic: TopicData | TopicDefinition,
    include_figure: bool = True,
) -> list[Indicator]:
    """Create indicator(s) for features of a GeoJSON FeatureCollection.

    Indicators are computed asynchronously utilizing semaphores.
    Properties of the input GeoJSON are preserved.
    """
    tasks: list[Coroutine] = []
    for i, feature in enumerate(bpolys.features):
        if feature.id is None:
            feature.id = i
        # Only enforce size limit if ohsome API data is not provided
        # Disable size limit for the Mapping Saturation indicator
        if isinstance(topic, TopicDefinition) and key not in [
            "mapping-saturation",
            "currentness",
        ]:
            validate_area(feature)
        tasks.append(_create_indicator(key, feature, topic, include_figure))
    return await gather_with_semaphore(tasks)


async def create_report(parameters: ReportRequest, key: str) -> FeatureCollection:
    """Create report(s) for features of a GeoJSON FeatureCollection."""

    features = []
    for i, feature in enumerate(parameters.bpolys.features):
        if feature.id is None:
            feature.id = i
        validate_area(feature)
        # Reports for a FeatureCollection are not created asynchronously (as it is
        # the case with indicators), because indicators of a report are created
        # asynchronously
        report = await _create_report(key, feature)
        features.append(report.as_feature())
    return FeatureCollection(type="FeatureCollection", features=features)


async def _create_indicator(
    key: str,
    feature: Feature,
    topic: Topic,
    include_figure: bool = True,
) -> Indicator:
    """Create an indicator from scratch."""
    logging.info("Indicator key:  {0:4}".format(key))
    logging.info("Topic key:     {0:4}".format(topic.key))
    logging.info("Feature id:     {0:4}".format(feature.id))

    indicator_class = get_class_from_key(class_type="indicator", key=key)
    indicator = indicator_class(topic, feature)
    print(feature)
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
    logging.info("Feature id:  {0:4}".format(feature.id))

    report_class = get_class_from_key(class_type="report", key=key)
    report = report_class(feature=feature)

    tasks: list[Coroutine] = []
    for indicator_key, topic_key in report.indicator_topic:
        topic = get_topic_preset(topic_key)
        tasks.append(_create_indicator(indicator_key, feature, topic))

    report.indicators = await gather_with_semaphore(tasks)
    report.combine_indicators()

    return report
