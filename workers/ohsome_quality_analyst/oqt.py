"""
Controller for the creation of Indicators and Reports.
Functions are triggert by the CLI and API.
"""
import logging
from typing import Optional

from asyncpg.exceptions import UndefinedTableError
from geojson import Feature

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.base.report import BaseReport
from ohsome_quality_analyst.utils.definitions import INDICATOR_LAYER
from ohsome_quality_analyst.utils.helper import name_to_class


async def create_indicator(
    indicator_name: str,
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
        if await indicator.preprocess():
            logging.info("Run calculation")
            if indicator.calculate():
                logging.info("Run figure creation")
                if indicator.create_figure():
                    pass

    async def from_database(dataset, feature_id) -> bool:
        """Create indicator by loading existing results from database"""
        try:
            return await db_client.load_indicator_results(
                indicator, dataset, feature_id
            )
        except UndefinedTableError:
            return False

    indicator_class = name_to_class(class_type="indicator", name=indicator_name)
    logging.info("Creating indicator ...")
    logging.info("Indicator name:\t" + indicator_name)
    logging.info("Layer name:\t" + layer_name)

    # from scratch
    if feature is not None and dataset is None and feature_id is None:
        indicator = indicator_class(layer_name=layer_name, feature=feature)
        await from_scratch()
    # from database
    elif dataset is not None and feature_id is not None:
        feature = await db_client.get_feature_from_db(dataset, feature_id, fid_field)
        indicator = indicator_class(layer_name=layer_name, feature=feature)
        success = await from_database(dataset, feature_id)
        if not success or force:
            await from_scratch()
            await db_client.save_indicator_results(indicator, dataset, feature_id)
    else:
        raise ValueError(
            "Invalid set of arguments for the creation of an indicator. "
            + "Either `feature` or `dataset` and `feature_id` has to be provided."
        )

    return indicator


async def create_all_indicators(force: bool = False) -> None:
    """Create all indicator/layer combination for OQT regions.

    Possible indicator/layer combinations are defined in `definitions.py`.
    """
    fids = await db_client.get_feature_ids("regions", "ogc_fid")
    for fid in fids:
        for indicator_name, layer_name in INDICATOR_LAYER:
            try:
                await create_indicator(
                    indicator_name,
                    layer_name,
                    dataset="regions",
                    feature_id=fid,
                    force=force,
                )
            # TODO: Those errors are raised during MappingCalculation creation.
            except (ValueError) as error:
                if indicator_name == "MappingSaturation":
                    logging.error(error)
                    logging.error(
                        f"Error occurred during creation of indicator "
                        f"'{indicator_name}' for OQT regions "
                        f"and feature id '{fid}'. "
                        f"Continue creation of indicators."
                    )
                    continue
                else:
                    raise (error)


async def create_report(
    report_name: str,
    force: bool = False,
    feature: Optional[Feature] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
) -> BaseReport:
    """Create a report.

    A Reports creates indicators from scratch or fetches them from the database.
    It then aggregates all indicators and calculates an overall quality score.
    """
    if feature is None and dataset is not None and feature_id is not None:
        feature = await db_client.get_feature_from_db(dataset, feature_id, fid_field)

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
