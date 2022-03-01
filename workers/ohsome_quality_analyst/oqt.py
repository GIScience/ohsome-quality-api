"""Controller for the creation of Indicators and Reports.

Functions are triggered by the CLI and API.
"""
import asyncio
import logging
from functools import singledispatch
from typing import List, Union

from asyncpg.exceptions import UndefinedTableError
from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorDatabase,
    ReportBpolys,
    ReportDatabase,
)
from ohsome_quality_analyst.base.indicator import BaseIndicator as Indicator
from ohsome_quality_analyst.base.report import BaseReport as Report
from ohsome_quality_analyst.utils.definitions import GEOM_SIZE_LIMIT, INDICATOR_LAYER
from ohsome_quality_analyst.utils.exceptions import (
    EmptyRecordError,
    SizeRestrictionError,
)
from ohsome_quality_analyst.utils.helper import loads_geojson, name_to_class


async def create_indicator_as_geojson(
    parameters: Union[IndicatorBpolys, IndicatorDatabase],
    force: bool = False,
    size_restriction: bool = False,
) -> Union[Feature, FeatureCollection]:
    """Create an indicator or multiple indicators as GeoJSON object.

    Returns:
        Depending on the input a single indicator as GeoJSON Feature will be returned
        or multiple indicators as GeoJSON FeatureCollection will be returned.
    """
    if isinstance(parameters, IndicatorBpolys):
        features = []
        for i, feature in enumerate(loads_geojson(parameters.bpolys)):
            if "id" in feature.keys():
                id_ = str(feature["id"])
            else:
                id_ = str(i)
            logging.info("Input feature identifier: " + id_)
            if size_restriction:
                await check_area_size(feature.geometry)
            indicator = await create_indicator(
                parameters.copy(update={"bpolys": feature}),
                force,
            )
            features.append(indicator.as_feature(flatten=True))
        if len(features) == 1:
            return features[0]
        else:
            return FeatureCollection(features=features)
    elif isinstance(parameters, IndicatorDatabase):
        indicator = await create_indicator(parameters, force)
        return indicator.as_feature(flatten=True)
    else:
        raise ValueError("Unexpected parameters: " + str(parameters))


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
            if "id" in feature.keys():
                id_ = str(feature["id"])
            else:
                id_ = str(i)
            logging.info("Input feature identifier: " + id_)
            if size_restriction:
                await check_area_size(feature.geometry)
            report = await create_report(
                parameters.copy(update={"bpolys": feature}),
                force,
            )
            features.append(report.as_feature())
        if len(features) == 1:
            return features[0]
        else:
            return FeatureCollection(features=features)
    elif isinstance(parameters, ReportDatabase):
        report = await create_report(parameters, force)
        return report.as_feature()
    else:
        raise ValueError("Unexpected parameters: " + str(parameters))


@singledispatch
async def create_indicator(parameters, force: bool = False) -> Indicator:
    """Create an Indicator."""
    raise NotImplementedError(
        "Cannot create Indicator for parameters of type: " + str(type(parameters))
    )


@create_indicator.register
async def _create_indicator(
    parameters: IndicatorDatabase,
    force: bool = False,
) -> Indicator:
    """Create an Indicator by fetching the results from the database.

    Fetch the pre-computed Indicator results from the Geodatabase.

    In case fetching the Indicator results from the database fails, the Indicator is
    created from scratch and then those results are saved to the database.
    """
    name = parameters.name.value
    layer_name = parameters.layer_name.value

    logging.info("Creating indicator ...")
    logging.info("Indicator name: " + name)
    logging.info("Layer name:     " + layer_name)

    dataset = parameters.dataset.value
    fid_field = parameters.fid_field
    if fid_field is not None:
        feature_id = await db_client.map_fid_to_uid(
            dataset,
            parameters.feature_id,
            fid_field.value,
        )
    else:
        feature_id = parameters.feature_id

    feature = await db_client.get_feature_from_db(dataset, feature_id)
    indicator_class = name_to_class(class_type="indicator", name=name)
    indicator_raw = indicator_class(layer_name=layer_name, feature=feature)
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
                layerName=layer_name,
                bpolys=feature,
            )
        )
        await db_client.save_indicator_results(indicator, dataset, feature_id)
    return indicator


@create_indicator.register
async def _create_indicator(  # noqa
    parameters: IndicatorBpolys,
    force: bool = False,
) -> Indicator:
    """Create an indicator from scratch."""
    name = parameters.name.value
    layer_name = parameters.layer_name.value
    feature = parameters.bpolys

    logging.info("Creating indicator ...")
    logging.info("Indicator name: " + name)
    logging.info("Layer name:     " + layer_name)

    indicator_class = name_to_class(class_type="indicator", name=name)
    indicator = indicator_class(layer_name, feature)

    logging.info("Run preprocessing")
    await indicator.preprocess()
    logging.info("Run calculation")
    indicator.calculate()
    logging.info("Run figure creation")
    indicator.create_figure()

    return indicator


@singledispatch
async def create_report(parameters, force: bool = False) -> Report:
    """Create a Report."""
    raise NotImplementedError(
        "Cannot create Report for parameters of type: " + str(type(parameters))
    )


@create_report.register
async def _create_report(
    parameters: ReportDatabase,
    force: bool = False,
) -> Report:
    """Create a Report.

    Fetches indicator results form the database.
    Aggregates all indicator results and calculates an overall quality score.
    """
    name = parameters.name.value

    logging.info("Creating Report...")
    logging.info("Report name: " + name)

    dataset = parameters.dataset.value
    fid_field = parameters.fid_field
    if fid_field is not None:
        feature_id = await db_client.map_fid_to_uid(
            dataset,
            parameters.feature_id,
            fid_field.value,
        )
    else:
        feature_id = parameters.feature_id

    feature = await db_client.get_feature_from_db(dataset, feature_id)
    report_class = name_to_class(class_type="report", name=name)
    report = report_class(feature=feature)
    report.set_indicator_layer()

    for indicator_name, layer_name in report.indicator_layer:
        indicator = await create_indicator(
            IndicatorDatabase(
                name=indicator_name,
                layerName=layer_name,
                dataset=dataset,
                featureId=feature_id,
            ),
            force=force,
        )
        report.indicators.append(indicator)
    report.combine_indicators()
    return report


@create_report.register
async def _create_report(  # noqa
    parameters: ReportBpolys,
    force: bool = False,
) -> Report:
    """Create a Report.

    Create indicators from scratch.
    Aggregates all indicator results and calculates an overall quality score.
    """
    name, feature = (
        parameters.name.value,
        parameters.bpolys,
    )

    logging.info("Creating Report...")
    logging.info("Report name: " + name)

    report_class = name_to_class(class_type="report", name=name)
    report = report_class(feature=feature)
    report.set_indicator_layer()

    for indicator_name, layer_name in report.indicator_layer:
        indicator = await create_indicator(
            IndicatorBpolys(
                name=indicator_name,
                layerName=layer_name,
                bpolys=feature,
            )
        )
        report.indicators.append(indicator)
    report.combine_indicators()
    return report


async def create_all_indicators(force: bool = False) -> None:
    """Create all Indicator/Layer combinations for OQT regions.

    Possible Indicator/Layer combinations are defined in `definitions.py`.
    This functions executes `create_indicator()` function up to four times concurrently.
    """

    async def _create_indicator(indicator_name, layer_name, fid, force, semaphore):
        async with semaphore:
            await create_indicator(
                IndicatorDatabase(
                    name=indicator_name,
                    layerName=layer_name,
                    dataset="regions",
                    featureId=fid,
                ),
                force=force,
            )

    # Semaphore limits num of concurrent executions
    semaphore = asyncio.Semaphore(4)
    tasks: List[asyncio.Task] = []
    fids = await db_client.get_feature_ids("regions")
    for fid in fids:
        for indicator_name, layer_name in INDICATOR_LAYER:
            tasks.append(
                asyncio.create_task(
                    _create_indicator(
                        indicator_name,
                        layer_name,
                        fid,
                        force,
                        semaphore,
                    )
                )
            )
    await asyncio.gather(*tasks)


async def check_area_size(geom: Union[Polygon, MultiPolygon]):
    if await db_client.get_area_of_bpolys(geom) > GEOM_SIZE_LIMIT:
        raise SizeRestrictionError(GEOM_SIZE_LIMIT)
