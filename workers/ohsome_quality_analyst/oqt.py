"""
Controller for the creation of Indicators and Reports.
Functions are triggert by the CLI and API.
"""
import logging

from geojson import FeatureCollection
from psycopg2.errors import UndefinedTable

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.utils.definitions import DATASET_NAMES, INDICATOR_LAYER
from ohsome_quality_analyst.utils.helper import (
    camel_to_snake,
    name_to_class,
    validate_geojson,
)


async def create_indicator(
    indicator_name: str = None,
    layer_name: str = None,
    bpolys: FeatureCollection = None,
    dataset: str = None,
    feature_id: int = None,
) -> object:
    """Create an indicator.

    An indicator is created by either calculating the indicator results
    for a geometry from scratch (bpolys) or by fetching indicator
    results from the geodatabase (dataset, feature_id).

    In case fetching indicator results from database does fail
    the indicator is created from scratch and the results are saved
    to the database.

    Returns:
        Indicator
    """
    logging.info("Creating indicator ...")
    if bpolys is not None:
        logging.info("Indicator name:\t" + indicator_name)
        logging.info("Layer name:\t" + layer_name)
        validate_geojson(bpolys)
    else:
        logging.info("Indicator name:\t" + indicator_name)
        logging.info("Layer name:\t" + layer_name)
        logging.info("Dataset name:\t" + dataset)
        logging.info("Feature id:\t" + str(feature_id))
    # Support only predefined datasets.
    # Otherwise creation of arbitrary relations (tables) are possible.
    if dataset is not None and dataset not in DATASET_NAMES:
        raise ValueError("Given dataset name does not exist: " + dataset)

    async def from_scratch():
        """Create indicatore from scratch."""
        logging.info("Run preprocessing")
        await indicator.preprocess()
        logging.info("Run calculation")
        indicator.calculate()
        logging.info("Run figure creation")
        indicator.create_figure()

    def from_database() -> bool:
        """Create indicator by loading existing results from database"""
        try:
            return db_client.load_indicator_results(indicator)
        except UndefinedTable:
            return False

    indicator_class = name_to_class(class_type="indicator", name=indicator_name)
    indicator = indicator_class(
        layer_name=layer_name, bpolys=bpolys, dataset=dataset, feature_id=feature_id
    )

    if bpolys is not None and dataset is None and feature_id is None:
        await from_scratch()
    elif dataset is not None and feature_id is not None:
        success = from_database()
        if not success:
            await from_scratch()
            db_client.save_indicator_results(indicator)
    return indicator


async def create_all_indicators(dataset: str, force: bool = False) -> None:
    """Create all indicator/layer combination for a dataset.

    Possible indicator/layer combinations are defined in `definitions.py`.
    """
    if force:
        for indicator_name, layer_name in INDICATOR_LAYER:
            indicator_name = camel_to_snake(indicator_name)
            db_client.drop_result_table(dataset, indicator_name, layer_name)

    fids = db_client.get_fid_list(dataset)
    for feature_id in fids:
        for indicator_name, layer_name in INDICATOR_LAYER:
            await create_indicator(
                indicator_name,
                layer_name,
                dataset=dataset,
                feature_id=feature_id,
            )


async def create_report(
    report_name: str,
    bpolys: FeatureCollection = None,
    dataset: str = None,
    feature_id: int = None,
) -> object:
    """Create a report.

    A Reports creates indicators from scratch or fetches them from the database.
    It then aggregates all indicators and calculates an overall quality scrore.

    Returns:
        Report
    """
    report_class = name_to_class(class_type="report", name=report_name)
    report = report_class(bpolys=bpolys, dataset=dataset, feature_id=feature_id)
    report.set_indicator_layer()
    for indicator_name, layer_name in report.indicator_layer:
        indicator = await create_indicator(
            indicator_name,
            layer_name,
            report.bpolys,
            report.dataset,
            report.feature_id,
        )
        report.indicators.append(indicator)
    report.combine_indicators()
    return report
