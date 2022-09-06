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
    ReportBpolys,
    ReportDatabase,
)
from ohsome_quality_analyst.base.indicator import BaseIndicator as Indicator
from ohsome_quality_analyst.base.layer import BaseLayer as Layer
from ohsome_quality_analyst.base.report import BaseReport as Report
from ohsome_quality_analyst.config import get_config_value
from ohsome_quality_analyst.definitions import (
    INDICATOR_LAYER,
    get_layer_definition,
    get_valid_indicators,
    get_valid_layers,
)
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
        if size_restriction and isinstance(parameters, IndicatorBpolys):
            await check_area_size(feature.geometry)
        tasks.append(create_indicator(parameters.copy(update={"bpolys": feature})))
    indicators = await gather_with_semaphore(tasks)
    features = [
        i.as_feature(
            parameters.flatten,
            parameters.include_data,
            parameters.include_svg,
            parameters.include_html,
        )
        for i in indicators
    ]
    if len(features) == 1:
        return features[0]
    else:
        return FeatureCollection(features=features)


@create_indicator_as_geojson.register(IndicatorDatabase)
async def _(
    parameters: IndicatorDatabase,
    force: bool = False,
    **_kwargs,
) -> Feature:
    """Create an indicator as GeoJSON object."""
    indicator = await create_indicator(parameters, force)
    return indicator.as_feature(
        parameters.flatten,
        parameters.include_data,
        parameters.include_svg,
        parameters.include_html,
    )


async def create_report_as_geojson(
    parameters: Union[ReportBpolys, ReportDatabase],
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
                force,
            )
            features.append(
                report.as_feature(
                    parameters.flatten,
                    parameters.include_data,
                    parameters.include_svg,
                    parameters.include_html,
                )
            )
        if len(features) == 1:
            return features[0]
        else:
            return FeatureCollection(features=features)
    elif isinstance(parameters, ReportDatabase):
        report = await create_report(parameters, force)
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
    *_args,
    force: bool = False,
) -> Indicator:
    """Create an Indicator by fetching the results from the database.

    Fetch the pre-computed Indicator results from the Geodatabase.

    In case fetching the Indicator results from the database fails, the Indicator is
    created from scratch and then those results are saved to the database.
    """
    name = parameters.name.value
    layer: Layer = get_layer_definition(parameters.layer_key.value)

    logging.info("Fetching Indicator from database ...")
    logging.info("Feature id:     {0:4}".format(parameters.feature_id))
    logging.info("Indicator name: {0:4}".format(name))
    logging.info("Layer name:     {0:4}".format(layer.name))

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
    indicator_class = name_to_class(class_type="indicator", name=name)
    indicator_raw = indicator_class(layer=layer, feature=feature)
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
                name=name,
                layerKey=parameters.layer_key.value,
                bpolys=feature,
            )
        )
        await db_client.save_indicator_results(indicator, dataset, feature_id)
    if parameters.include_html:
        indicator.create_html()
    return indicator


@create_indicator.register
async def _(
    parameters: IndicatorBpolys,
    *_args,
) -> Indicator:
    """Create an indicator from scratch."""
    name = parameters.name.value
    layer: Layer = get_layer_definition(parameters.layer_key.value)
    feature = parameters.bpolys

    logging.info("Calculating Indicator for custom AOI ...")
    logging.info("Feature id:     {0:4}".format(feature.get("id", 1)))
    logging.info("Indicator name: {0:4}".format(name))
    logging.info("Layer name:     {0:4}".format(layer.name))

    indicator_class = name_to_class(class_type="indicator", name=name)
    indicator = indicator_class(layer, feature)

    logging.info("Run preprocessing")
    await indicator.preprocess()
    logging.info("Run calculation")
    indicator.calculate()
    logging.info("Run figure creation")
    indicator.create_figure(include_svg=parameters.include_svg)
    if parameters.include_html:
        indicator.create_html()

    return indicator


@create_indicator.register
async def _(
    parameters: IndicatorData,
    *_args,
) -> Indicator:
    """Create an indicator from scratch."""
    name = parameters.name.value
    layer = parameters.layer
    feature = parameters.bpolys

    logging.info("Calculating Indicator with custom Layer ...")
    logging.info("Feature id:     {0:4}".format(feature.get("id", 1)))
    logging.info("Indicator name: {0:4}".format(name))
    logging.info("Layer name:     {0:4}".format(layer.name))

    indicator_class = name_to_class(class_type="indicator", name=name)
    indicator = indicator_class(layer, feature)

    logging.info("Run preprocessing")
    await indicator.preprocess()
    logging.info("Run calculation")
    indicator.calculate()
    logging.info("Run figure creation")
    indicator.create_figure(include_svg=parameters.include_svg)
    if parameters.include_html:
        indicator.create_html()

    return indicator


@singledispatch
async def create_report(parameters) -> Report:
    """Create a Report."""
    raise NotImplementedError(
        "Cannot create Report for parameters of type: " + str(type(parameters))
    )


@create_report.register
async def _(parameters: ReportDatabase, force: bool = False) -> Report:
    """Create a Report.

    Fetches indicator results form the database.
    Aggregates all indicator results and calculates an overall quality score.

    Indicators for a Report are created asynchronously utilizing semaphores.
    """
    name = parameters.name.value

    logging.info("Creating Report...")
    logging.info("Feature id:  {0:4}".format(parameters.feature_id))
    logging.info("Report name: {0:4}".format(name))

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
    report_class = name_to_class(class_type="report", name=name)
    report = report_class(feature=feature)
    report.set_indicator_layer()

    tasks: List[Coroutine] = []
    for indicator_name, layer_key in report.indicator_layer:
        tasks.append(
            create_indicator(
                IndicatorDatabase(
                    name=indicator_name,
                    layerKey=layer_key,
                    dataset=dataset,
                    featureId=feature_id,
                ),
                force=force,
            )
        )
    report.indicators = await gather_with_semaphore(tasks)
    report.combine_indicators()
    if parameters.include_html:
        report.create_html(include_html=parameters.include_html)
    return report


@create_report.register
async def _(parameters: ReportBpolys, *_args) -> Report:
    """Create a Report.

    Aggregates all indicator results and calculates an overall quality score.

    Indicators for a Report are created asynchronously utilizing semaphores.
    """
    name, feature = (
        parameters.name.value,
        parameters.bpolys,
    )

    logging.info("Creating Report...")
    logging.info("Feature id:  {0:4}".format(feature.get("id", 1)))
    logging.info("Report name: {0:4}".format(name))

    report_class = name_to_class(class_type="report", name=name)
    report = report_class(feature=feature)
    report.set_indicator_layer()

    tasks: List[Coroutine] = []
    for indicator_name, layer_key in report.indicator_layer:
        tasks.append(
            create_indicator(
                IndicatorBpolys(
                    name=indicator_name,
                    layerKey=layer_key,
                    bpolys=feature,
                ),
            )
        )
    report.indicators = await gather_with_semaphore(tasks)
    report.combine_indicators()
    report.create_html(include_html=parameters.include_html)
    return report


async def create_all_indicators(
    dataset: str,
    indicator_name: Optional[str] = None,
    layer_key: Optional[str] = None,
    force: bool = False,
) -> None:
    """Create all indicator/layer combination for the given dataset.

    Possible Indicator/Layer combinations are defined in `definitions.py`.
    This functions executes `create_indicator()` function up to four times concurrently.
    """
    if indicator_name is not None and layer_key is None:
        layers = get_valid_layers(indicator_name)
        indicator_layer = [(indicator_name, lay) for lay in layers]
    elif indicator_name is None and layer_key is not None:
        indicators = get_valid_indicators(layer_key)
        indicator_layer = [(ind, layer_key) for ind in indicators]
    elif indicator_name is not None and layer_key is not None:
        indicator_layer = [(indicator_name, layer_key)]
    else:
        indicator_layer = INDICATOR_LAYER

    tasks: List[asyncio.Task] = []
    fids = await db_client.get_feature_ids(dataset)
    for fid in fids:
        for indicator_name_, layer_key_ in indicator_layer:
            tasks.append(
                create_indicator(
                    IndicatorDatabase(
                        name=indicator_name_,
                        layerKey=layer_key_,
                        dataset=dataset,
                        featureId=fid,
                    ),
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
