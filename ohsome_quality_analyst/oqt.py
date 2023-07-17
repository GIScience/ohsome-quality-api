"""Controller for computing Indicators and Reports."""

import logging
from typing import Coroutine

from geojson import Feature, FeatureCollection

from ohsome_quality_analyst.api.request_models import (
    IndicatorDataRequest,
    IndicatorRequest,
    ReportRequest,
)
from ohsome_quality_analyst.definitions import get_topic_definition
from ohsome_quality_analyst.indicators.base import BaseIndicator as Indicator
from ohsome_quality_analyst.reports.base import BaseReport as Report
from ohsome_quality_analyst.utils.helper import get_class_from_key, loads_geojson
from ohsome_quality_analyst.utils.helper_asyncio import gather_with_semaphore
from ohsome_quality_analyst.utils.validators import validate_area


async def create_indicator_as_geojson(
    parameters: IndicatorRequest | IndicatorDataRequest,
    key: str,
) -> Feature | FeatureCollection:
    """Create an indicator or multiple indicators as GeoJSON object.

    Indicators for a FeatureCollection are created asynchronously utilizing semaphores.

    Returns:
        Depending on the input a single indicator as GeoJSON Feature will be returned
        or multiple indicators as GeoJSON FeatureCollection will be returned.
    """
    tasks: list[Coroutine] = []
    for i, feature in enumerate(loads_geojson(parameters.bpolys)):
        if "id" not in feature.keys():
            feature["id"] = i
        # Only enforce size limit if ohsome API data is not provided
        # Disable size limit for the Mapping Saturation indicator
        if isinstance(parameters, IndicatorRequest) and key != "mapping-saturation":
            validate_area(feature)
        tasks.append(
            create_indicator(parameters.copy(update={"bpolys": feature}), key=key)
        )
    indicators = await gather_with_semaphore(tasks)
    features = [i.as_feature(parameters.include_data) for i in indicators]
    return FeatureCollection(features=features)


async def create_report_as_geojson(
    parameters: ReportRequest,
    key: str,
) -> Feature | FeatureCollection:
    """Create a report or multiple reports as GeoJSON object.

    Returns:
        Depending on the input a single report as GeoJSON Feature will be returned
        or multiple reports as GeoJSON FeatureCollection will be returned.
    """
    features = []
    for i, feature in enumerate(loads_geojson(parameters.bpolys)):
        if "id" not in feature.keys():
            feature["id"] = i
        validate_area(feature)
        # Reports for a FeatureCollection are not created asynchronously (as it is
        # the case with indicators), because indicators of a report are created
        # asynchronously
        report = await create_report(
            parameters.copy(update={"bpolys": feature}),
            key,
        )
        features.append(report.as_feature(parameters.include_data))
    if len(features) == 1:
        return features[0]
    else:
        return FeatureCollection(features=features)


async def create_indicator(
    parameters: IndicatorRequest | IndicatorDataRequest,
    key: str,
) -> Indicator:
    """Create an indicator from scratch."""
    if isinstance(parameters, IndicatorDataRequest):
        topic = parameters.topic
    else:
        topic = get_topic_definition(parameters.topic_key.value)
    feature = parameters.bpolys

    logging.info("Calculating Indicator for custom AOI ...")
    logging.info("Feature id:     {0:4}".format(feature.get("id", 1)))
    logging.info("Indicator key:  {0:4}".format(key))
    logging.info("Topic name:     {0:4}".format(topic.name))

    indicator_class = get_class_from_key(class_type="indicator", key=key)
    indicator = indicator_class(topic, feature)

    logging.info("Run preprocessing")
    await indicator.preprocess()
    logging.info("Run calculation")
    indicator.calculate()
    logging.info("Run figure creation")
    indicator.create_figure()
    indicator.create_html()

    return indicator


async def create_report(parameters: ReportRequest, key: str) -> Report:
    """Create a Report.

    Aggregates all indicator results and calculates an overall quality score.

    Indicators for a Report are created asynchronously utilizing semaphores.
    """
    feature = parameters.bpolys

    logging.info("Creating Report...")
    logging.info("Feature id:  {0:4}".format(feature.get("id", 1)))
    logging.info("Report key:  {0:4}".format(key))

    report_class = get_class_from_key(class_type="report", key=key)
    report = report_class(feature=feature)

    tasks: list[Coroutine] = []
    for indicator_key, topic_key in report.indicator_topic:
        tasks.append(
            create_indicator(
                IndicatorRequest(
                    topic=topic_key,
                    bpolys=feature,
                ),
                key=indicator_key,
            )
        )
    report.indicators = await gather_with_semaphore(tasks)
    report.combine_indicators()
    report.create_html()
    return report
