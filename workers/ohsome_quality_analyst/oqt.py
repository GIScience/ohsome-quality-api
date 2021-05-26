"""
Controller for the creation of Indicators and Reports.
Functions are triggert by the CLI and API.
"""
import logging

from asyncpg.exceptions import UndefinedTableError
from geojson import FeatureCollection
from Typing import Optional, Union

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.base.indicator import BaseIndicator
from ohsome_quality_analyst.utils.definitions import DATASETS, INDICATOR_LAYER
from ohsome_quality_analyst.utils.helper import name_to_class


async def create_indicator(
    indicator_name: str,
    layer_name: str,
    force: bool = False,
    bpolys: Optional[FeatureCollection] = None,
    dataset: Optional[str] = None,
    id_: Optional[Union[int, str]] = None,
    id_field: Optional[str] = None,
) -> BaseIndicator:
    """Create an indicator.

    An indicator can be created in two ways:

    One; Calculate from scratch for an area of interest.
    This is done by providing a bounding polygon as input parameter.

    Two; Fetch the pre-computed results from the Geodatabase.
    This is done by providing the dataset name and feature id as input parameter.

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
    if bpolys is not None and dataset is None and id_ is None:
        indicator = indicator_class(layer_name=layer_name, bpolys=bpolys)
        await from_scratch()
    # from database
    elif bpolys is None and dataset is not None and id_ is not None:
        logging.info("Dataset name:\t" + dataset)
        logging.info("Feature id:\t" + str(id_))

        if id_field is None:
            id_field = DATASETS[dataset]["default"]

        # Support only predefined datasets and id field.
        # Otherwise creation of arbitrary relations or SQL injections are possible.
        if dataset not in DATASETS.keys():
            raise ValueError("Input dataset is not valid")
        if (
            id_field not in DATASETS[dataset]["others"]
            or id_field != DATASETS[dataset]["default"]
        ):
            # TODO: Raise custom exception?
            raise ValueError

        bpolys = await db_client.get_bpolys_from_db(dataset, id_field, id_)

        indicator = indicator_class(layer_name=layer_name, bpolys=bpolys)
        success = await from_database(dataset, id_)
        if not success or force:
            await from_scratch()
            await db_client.save_indicator_results(indicator, dataset, id_)
    else:
        raise ValueError("Invalid set of arguments for the creation of an indicator")

    return indicator


async def create_all_indicators(dataset: str, force: bool = False) -> None:
    """Create all indicator/layer combination for a dataset.

    Possible indicator/layer combinations are defined in `definitions.py`.
    """
    fids = await db_client.get_fids(dataset)
    for feature_id in fids:
        for indicator_name, layer_name in INDICATOR_LAYER:
            try:
                await create_indicator(
                    indicator_name,
                    layer_name,
                    dataset=dataset,
                    feature_id=feature_id,
                    force=force,
                )
            # TODO: Those errors are raised during MappingCalculation creation.
            except (ValueError) as error:
                if indicator_name == "MappingSaturation":
                    logging.error(error)
                    logging.error(
                        f"Error occurred during creation of indicator "
                        f"'{indicator_name}' for the dataset '{dataset}' "
                        f"and feature_id '{feature_id}'. "
                        f"Continue creation of indicators."
                    )
                    continue
                else:
                    raise (error)


async def create_report(
    report_name: str,
    bpolys: FeatureCollection = None,
    dataset: str = None,
    feature_id: int = None,
    force: bool = False,
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
            force=force,
        )
        report.indicators.append(indicator)
    report.combine_indicators()
    return report
