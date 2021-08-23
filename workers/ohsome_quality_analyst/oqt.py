"""
Controller for the creation of Indicators and Reports.
Functions are triggert by the CLI and API.
"""
import asyncio
import logging
from typing import List, Optional, Union

from asyncpg.exceptions import UndefinedTableError
from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.report import BaseReport
from ohsome_quality_analyst.utils.definitions import GEOM_SIZE_LIMIT, INDICATOR_LAYER
from ohsome_quality_analyst.utils.helper import loads_geojson, name_to_class


async def create_indicator_as_geojson(
    name: str,
    layer_name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
    force: bool = False,
    size_restriction: bool = False,
) -> Union[Feature, FeatureCollection]:
    """Create an indicator or multiple indicators as GeoJSON object.

    Depending on the input a single indicator as GeoJSON Feature will be returned
    or multiple indicators as GeoJSON FeatureCollection will be returned.
    """
    if bpolys is not None:
        features = []
        for i, feature in enumerate(loads_geojson(bpolys)):
            logging.info("Input feature index: " + str(i))
            if size_restriction:
                await check_area_size(feature.geometry)
            indicator = await create_indicator(
                name,
                layer_name,
                feature,
                dataset,
                feature_id,
                fid_field,
                force,
            )
            features.append(indicator.as_feature())
        if len(features) == 1:
            return features[0]
        else:
            return FeatureCollection(features=features)
    else:
        # When using a dataset and feature id as input
        indicator = await create_indicator(
            name,
            layer_name,
            bpolys,
            dataset,
            feature_id,
            fid_field,
            force,
        )
        return indicator.as_feature()


async def create_report_as_geojson(
    name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
    force: bool = False,
    size_restriction: bool = False,
) -> Union[Feature, FeatureCollection]:
    """Create a report multiple reports as GeoJSON object.

    Depending on the input a single report as GeoJSON Feature will be returned
    or multiple reports as GeoJSON FeatureCollection will be returned.
    """
    if bpolys is not None:
        features = []
        for i, feature in enumerate(loads_geojson(bpolys)):
            logging.info("Input feature index: " + str(i))
            if size_restriction:
                await check_area_size(feature.geometry)
            report = await create_report(
                name,
                feature,
                dataset,
                feature_id,
                fid_field,
                force,
            )
            features.append(report.as_feature())
        if len(features) == 1:
            return features[0]
        else:
            return FeatureCollection(features=features)
    else:
        # When using a dataset and feature id as input
        report = await create_report(
            name,
            bpolys,
            dataset,
            feature_id,
            fid_field,
            force,
        )
        return report.as_feature()


async def create_indicator(
    name: str,
    layer_name: str,
    feature: Optional[Feature] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
    force: bool = False,
) -> BaseIndicator:
    """Create an indicator.

    An indicator can be created in two ways:

    1. From Scratch: Calculate from scratch for an area of interest.
    This is done by providing a GeoJSON Feature as input parameter.

    2. From Database: Fetch the pre-computed results from the Geodatabase.
    This is done by providing the dataset name and feature id as input parameter.

    If both a GeoJSON Feature and dataset + feature id are given,
    the second way will be executed.

    In the case that fetching indicator results from database does fail
    the indicator is created from scratch and the results are saved
    to the database.
    """

    async def from_scratch() -> None:
        """Create indicatore from scratch."""
        logging.info("Run preprocessing")
        await indicator.preprocess()
        logging.info("Run calculation")
        indicator.calculate()
        logging.info("Run figure creation")
        indicator.create_figure()

    async def from_database(dataset, feature_id) -> bool:
        """Create indicator by loading existing results from database"""
        try:
            return await db_client.load_indicator_results(
                indicator, dataset, feature_id
            )
        except UndefinedTableError:
            return False

    indicator_class = name_to_class(class_type="indicator", name=name)
    logging.info("Creating indicator ...")
    logging.info("Indicator name: " + name)
    logging.info("Layer name:     " + layer_name)

    # from scratch
    if feature is not None and dataset is None and feature_id is None:
        indicator = indicator_class(layer_name, feature)
        await from_scratch()
    # from database
    elif dataset is not None and feature_id is not None:
        if fid_field is not None:
            feature_id = await db_client.map_fid_to_uid(dataset, feature_id, fid_field)
        feature = await db_client.get_feature_from_db(dataset, feature_id)
        indicator = indicator_class(layer_name=layer_name, feature=feature)
        success = await from_database(dataset, feature_id)
        if not success or force:
            await from_scratch()
            await db_client.save_indicator_results(indicator, dataset, feature_id)
    else:
        raise ValueError(
            "Invalid set of arguments for the creation of an indicator. "
            "Either `feature` or `dataset` and `feature_id` has to be provided."
        )

    return indicator


async def create_report(
    report_name: str,
    feature: Optional[Feature] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
    force: bool = False,
) -> BaseReport:
    """Create a report.

    A Reports creates indicators from scratch or fetches them from the database.
    It then aggregates all indicators and calculates an overall quality score.
    """
    logging.info("Creating Report...")
    logging.info("Report name: " + report_name)

    if feature is None and dataset is not None and feature_id is not None:
        if fid_field is not None:
            feature_id = await db_client.map_fid_to_uid(dataset, feature_id, fid_field)
            fid_field = None
        feature = await db_client.get_feature_from_db(dataset, feature_id)

    report_class = name_to_class(class_type="report", name=report_name)
    report = report_class(
        feature=feature, dataset=dataset, feature_id=feature_id, fid_field=fid_field
    )
    report.set_indicator_layer()
    for indicator_name, layer_name in report.indicator_layer:
        indicator = await create_indicator(
            indicator_name,
            layer_name,
            feature=report.feature,
            dataset=report.dataset,
            feature_id=report.feature_id,
            fid_field=fid_field,
            force=force,
        )
        report.indicators.append(indicator)
    report.combine_indicators()
    return report


async def create_all_indicators(force: bool = False) -> None:
    """Create all indicator/layer combination for OQT regions.

    Possible indicator/layer combinations are defined in `definitions.py`.
    This functions executes `create_indicator()` function up to four times concurrently.
    """

    async def _create_indicator(indicator_name, layer_name, fid, force, semaphore):
        async with semaphore:
            await create_indicator(
                indicator_name,
                layer_name,
                dataset="regions",
                feature_id=fid,
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
    return await asyncio.gather(*tasks)


async def check_area_size(geom: Union[Polygon, MultiPolygon]):
    if await db_client.get_area_of_bpolys(geom) > GEOM_SIZE_LIMIT:
        raise ValueError(
            "Input GeoJSON Object is too big. "
            "The area should be less than {0} km².".format(GEOM_SIZE_LIMIT)
        )
