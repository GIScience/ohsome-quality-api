"""Controller for the creation of Indicators and Reports.

Functions are triggered by the CLI and API.
"""
import asyncio
import logging
from functools import singledispatch
from typing import Coroutine, List, Optional, Union

from asyncpg.exceptions import UndefinedTableError
from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorData,
    IndicatorDatabase,
    IndicatorEnum,
    ReportBpolys,
    ReportDatabase,
    ReportEnum,
)
from ohsome_quality_analyst.config import get_config_value
from ohsome_quality_analyst.definitions import (
    get_indicator_names,
    get_topic_definition,
    get_valid_indicators,
    get_valid_topics,
)
from ohsome_quality_analyst.indicators.base import BaseIndicator as Indicator
from ohsome_quality_analyst.reports.base import BaseReport as Report
from ohsome_quality_analyst.topics.models import BaseTopic as Topic
from ohsome_quality_analyst.utils.exceptions import (
    EmptyRecordError,
    SizeRestrictionError,
)
from ohsome_quality_analyst.utils.helper import loads_geojson, name_to_class
from ohsome_quality_analyst.utils.helper_asyncio import (
    filter_exceptions,
    gather_with_semaphore,
)


@singledispatch
async def create_indicator_as_geojson(parameters):
    raise NotImplementedError(
        "Cannot create Indicator as GeoJSON for parameters of type: "
        + str(type(parameters))
    )


@create_indicator_as_geojson.register(IndicatorBpolys)
@create_indicator_as_geojson.register(IndicatorData)
async def _(
    parameters: Union[IndicatorBpolys, IndicatorData],
    key: IndicatorEnum,
    size_restriction: bool = False,
    **_kwargs,
) -> Union[Feature, FeatureCollection]:
    """Create an indicator or multiple indicators as GeoJSON object.

    Indicators for a FeatureCollection are created asynchronously utilizing semaphores.

    Returns:
        Depending on the input a single indicator as GeoJSON Feature will be returned
        or multiple indicators as GeoJSON FeatureCollection will be returned.
    """
    tasks: List[Coroutine] = []
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
            await check_area_size(feature.geometry)
        tasks.append(
            create_indicator(parameters.copy(update={"bpolys": feature}), key=key)
        )
    indicators = await gather_with_semaphore(tasks)
    features = [
        i.as_feature(parameters.flatten, parameters.include_data) for i in indicators
    ]
    if len(features) == 1:
        return features[0]
    else:
        return FeatureCollection(features=features)


@create_indicator_as_geojson.register(IndicatorDatabase)
async def _(
    parameters: IndicatorDatabase,
    key: IndicatorEnum,
    force: bool = False,
    **_kwargs,
) -> Feature:
    """Create an indicator as GeoJSON object."""
    indicator = await create_indicator(parameters, key, force)
    return indicator.as_feature(parameters.flatten, parameters.include_data)


async def create_report_as_geojson(
    parameters: Union[ReportBpolys, ReportDatabase],
    key: ReportEnum,
    force: bool = False,
    size_restriction: bool = False,
) -> Union[Feature, FeatureCollection]:
    """Create a report or multiple reports as GeoJSON object.

    Returns:
        Depending on the input a single report as GeoJSON Feature will be returned
        or multiple reports as GeoJSON FeatureCollection will be returned.
    """
    if isinstance(parameters, ReportBpolys):
        features = []
        for i, feature in enumerate(loads_geojson(parameters.bpolys)):
            if "id" not in feature.keys():
                feature["id"] = i
            if size_restriction:
                await check_area_size(feature.geometry)
            # Reports for a FeatureCollection are not created asynchronously (as it is
            # the case with indicators), because indicators of a report are created
            # asynchronously
            report = await create_report(
                parameters.copy(update={"bpolys": feature}),
                key,
                force,
            )
            features.append(
                report.as_feature(parameters.flatten, parameters.include_data)
            )
        if len(features) == 1:
            return features[0]
        else:
            return FeatureCollection(features=features)
    elif isinstance(parameters, ReportDatabase):
        report = await create_report(parameters, key, force)
        return report.as_feature(parameters.flatten, parameters.include_data)
    else:
        raise ValueError("Unexpected parameters: " + str(parameters))


@singledispatch
async def create_indicator(parameters) -> Indicator:
    raise NotImplementedError(
        "Cannot create Indicator for parameters of type: " + str(type(parameters))
    )


@create_indicator.register
async def _(
    parameters: IndicatorDatabase,
    key: IndicatorEnum,
    force: bool = False,
) -> Indicator:
    """Create an Indicator by fetching the results from the database.

    Fetch the pre-computed Indicator results from the Geodatabase.

    In case fetching the Indicator results from the database fails, the Indicator is
    created from scratch and then those results are saved to the database.
    """
    topic: Topic = get_topic_definition(parameters.topic_key.value)

    logging.info("Fetching Indicator from database ...")
    logging.info("Feature id:     {0:4}".format(parameters.feature_id))
    logging.info("Indicator key: {0:4}".format(key)),
    logging.info("Topic name:     {0:4}".format(topic.name))

    dataset = parameters.dataset.value
    if parameters.fid_field is not None:
        feature_id = await db_client.map_fid_to_uid(
            dataset,
            parameters.feature_id,
            parameters.fid_field.value,
        )
    else:
        feature_id = parameters.feature_id
    feature = await db_client.get_feature_from_db(dataset, feature_id)
    indicator_class = name_to_class(class_type="indicator", name=key)
    indicator_raw = indicator_class(topic=topic, feature=feature)
    failure = False
    try:
        indicator = await db_client.load_indicator_results(
            indicator_raw,
            dataset,
            feature_id,
        )
    except (UndefinedTableError, EmptyRecordError):
        failure = True
    if force or failure:
        indicator = await create_indicator(
            IndicatorBpolys(
                topic=parameters.topic_key.value,
                bpolys=feature,
            ),
            key=key,
        )
        await db_client.save_indicator_results(indicator, dataset, feature_id)
    indicator.create_html()
    return indicator


@create_indicator.register
async def _(
    parameters: IndicatorBpolys,
    key: IndicatorEnum,
    *_args,
) -> Indicator:
    """Create an indicator from scratch."""
    topic: Topic = get_topic_definition(parameters.topic_key.value)
    feature = parameters.bpolys

    logging.info("Calculating Indicator for custom AOI ...")
    logging.info("Feature id:     {0:4}".format(feature.get("id", 1)))
    logging.info("Indicator key: {0:4}".format(key))
    logging.info("Topic name:     {0:4}".format(topic.name))

    indicator_class = name_to_class(class_type="indicator", name=key)
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
    key: IndicatorEnum,
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
    logging.info("Indicator key: {0:4}".format(key))
    logging.info("Topic name:     {0:4}".format(topic.name))

    indicator_class = name_to_class(class_type="indicator", name=key)
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
async def _(parameters: ReportDatabase, key: ReportEnum, force: bool = False) -> Report:
    """Create a Report.

    Fetches indicator results form the database.
    Aggregates all indicator results and calculates an overall quality score.

    Indicators for a Report are created asynchronously utilizing semaphores.
    """
    logging.info("Creating Report...")
    logging.info("Feature id:  {0:4}".format(parameters.feature_id))
    logging.info("Report key: {0:4}".format(key))

    dataset = parameters.dataset.value
    if parameters.fid_field is not None:
        feature_id = await db_client.map_fid_to_uid(
            dataset,
            parameters.feature_id,
            parameters.fid_field.value,
        )
    else:
        feature_id = parameters.feature_id

    feature = await db_client.get_feature_from_db(dataset, feature_id)
    report_class = name_to_class(class_type="report", name=key)
    report = report_class(feature=feature)

    tasks: List[Coroutine] = []
    for indicator_key, topic_key in report.indicator_topic:
        tasks.append(
            create_indicator(
                IndicatorDatabase(
                    topic=topic_key,
                    dataset=dataset,
                    feature_id=feature_id,
                ),
                key=indicator_key,
                force=force,
            )
        )
    report.indicators = await gather_with_semaphore(tasks)
    report.combine_indicators()
    report.create_html()
    return report


@create_report.register
async def _(parameters: ReportBpolys, key: ReportEnum, *_args) -> Report:
    """Create a Report.

    Aggregates all indicator results and calculates an overall quality score.

    Indicators for a Report are created asynchronously utilizing semaphores.
    """
    feature = parameters.bpolys

    logging.info("Creating Report...")
    logging.info("Feature id:  {0:4}".format(feature.get("id", 1)))
    logging.info("Report key: {0:4}".format(key))

    report_class = name_to_class(class_type="report", name=key)
    report = report_class(feature=feature)

    tasks: List[Coroutine] = []
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


async def create_all_indicators(
    dataset: str,
    indicator_name: Optional[str] = None,
    topic_key: Optional[str] = None,
    force: bool = False,
) -> None:
    """Create all indicator/topic combination for the given dataset.

    Possible Indicator/Topic combinations are defined in `definitions.py`.
    This functions executes `create_indicator()` function up to four times concurrently.
    """
    if indicator_name is not None and topic_key is None:
        topics = get_valid_topics(indicator_name)
        indicator_topic = [(indicator_name, lay) for lay in topics]
    elif indicator_name is None and topic_key is not None:
        indicators = get_valid_indicators(topic_key)
        indicator_topic = [(ind, topic_key) for ind in indicators]
    elif indicator_name is not None and topic_key is not None:
        indicator_topic = [(indicator_name, topic_key)]
    else:
        indicator_topic = []
        for indicator in get_indicator_names():
            for topic in get_valid_topics(indicator):
                indicator_topic.append((indicator, topic))

    tasks: List[asyncio.Task] = []
    fids = await db_client.get_feature_ids(dataset)
    for fid in fids:
        for indicator_key_, topic_key_ in indicator_topic:
            tasks.append(
                create_indicator(
                    IndicatorDatabase(
                        topic=topic_key_,
                        dataset=dataset,
                        feature_id=fid,
                    ),
                    key=indicator_key_,
                    force=force,
                )
            )
    # Do no raise exceptions. Filter out exceptions from result list and log them.
    results = await gather_with_semaphore(tasks, return_exceptions=True)
    exceptions = filter_exceptions(results)
    for exception in exceptions:
        message = getattr(exception, "message", repr(exception))
        logging.warning("Ignoring error: {0}".format(message))


async def check_area_size(geom: Union[Polygon, MultiPolygon]):
    if await db_client.get_area_of_bpolys(geom) > get_config_value("geom_size_limit"):
        raise SizeRestrictionError(get_config_value("geom_size_limit"))
