"""Controller for the creation of Indicators and Reports.

Functions are triggered by the API.
"""
import logging
from functools import singledispatch
from typing import Coroutine

from geojson import Feature, FeatureCollection

from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorData,
    ReportBpolys,
)
from ohsome_quality_analyst.definitions import get_topic_definition
from ohsome_quality_analyst.indicators.base import BaseIndicator as Indicator
from ohsome_quality_analyst.reports.base import BaseReport as Report
from ohsome_quality_analyst.topics.models import BaseTopic as Topic
from ohsome_quality_analyst.utils.helper import get_class_from_key, loads_geojson
from ohsome_quality_analyst.utils.helper_asyncio import gather_with_semaphore
from ohsome_quality_analyst.utils.validators import validate_area


@singledispatch
async def create_indicator_as_geojson(parameters):
    raise NotImplementedError(
        "Cannot create Indicator as GeoJSON for parameters of type: "
        + str(type(parameters))
    )


@create_indicator_as_geojson.register(IndicatorBpolys)
@create_indicator_as_geojson.register(IndicatorData)
async def _(
    parameters: IndicatorBpolys | IndicatorData,
    key: str,
    size_restriction: bool = False,
    **_kwargs,
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
        if (
            size_restriction
            and isinstance(parameters, IndicatorBpolys)
            and key != "mapping-saturation"
        ):
            validate_area(feature)
        tasks.append(
            create_indicator(parameters.copy(update={"bpolys": feature}), key=key)
        )
    indicators = await gather_with_semaphore(tasks)
    features = [i.as_feature(parameters.include_data) for i in indicators]
    return FeatureCollection(features=features)


async def create_report_as_geojson(
    parameters: ReportBpolys,
    key: str,
    force: bool = False,
    size_restriction: bool = False,
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
        if size_restriction:
            validate_area(feature)
        # Reports for a FeatureCollection are not created asynchronously (as it is
        # the case with indicators), because indicators of a report are created
        # asynchronously
        report = await create_report(
            parameters.copy(update={"bpolys": feature}),
            key,
            force,
        )
        features.append(report.as_feature(parameters.include_data))
    if len(features) == 1:
        return features[0]
    else:
        return FeatureCollection(features=features)


@singledispatch
async def create_indicator(parameters) -> Indicator:
    raise NotImplementedError(
        "Cannot create Indicator for parameters of type: " + str(type(parameters))
    )


@create_indicator.register
async def _(
    parameters: IndicatorBpolys,
    key: str,
    *_args,
) -> Indicator:
    """Create an indicator from scratch."""
    topic: Topic = get_topic_definition(parameters.topic_key.value)
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


@create_indicator.register
async def _(
    parameters: IndicatorData,
    key: str,
    *_args,
) -> Indicator:
    """Create an indicator from scratch."""
    if key != "mapping-saturation":
        raise ValueError(
            "Computing an Indicator for a Topic with data attached is only "
            + "supported for the Mapping Saturation Indicator."
        )
    topic = parameters.topic
    feature = parameters.bpolys

    logging.info("Calculating Indicator with custom Topic ...")
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
    if hasattr(indicator, "create_figure_plotly"):
        indicator.create_figure_plotly()
    indicator.create_html()

    return indicator


@singledispatch
async def create_report(parameters) -> Report:
    """Create a Report."""
    raise NotImplementedError(
        "Cannot create Report for parameters of type: " + str(type(parameters))
    )


@create_report.register
async def _(parameters: ReportBpolys, key: str, *_args) -> Report:
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
                IndicatorBpolys(
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
