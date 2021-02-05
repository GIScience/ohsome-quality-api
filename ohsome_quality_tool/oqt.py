"""
Controller for the creation of Indicators and Reports.
Functions are triggert by the CLI and API.
"""

from geojson import FeatureCollection
from psycopg2.errors import UndefinedTable

from ohsome_quality_tool.geodatabase.client import (
    get_fid_list,
    load_indicator_results,
    save_indicator_results,
)
from ohsome_quality_tool.utils.definitions import DATASET_NAMES, logger
from ohsome_quality_tool.utils.helper import name_to_class


def create_indicator(
    indicator_name: str,
    layer_name: str,
    bpolys: FeatureCollection = None,
    dataset: str = None,
    feature_id: int = None,
) -> object:
    """Create an indicator.

    An indicator is created by either calculating the indicator results
    for a geometry from scratch (bpolys) or by fetching indicator
    results from the geodatabase (dataset, feature_id).

    In case fetching indicator results from database does fail
    the indicator is create from scratch and the results are saved
    to the database.

    Returns:
        Indicator object
    """
    # Support only predefined datasets.
    # Otherwise creation of arbitrary relations (tables) are possible.
    if dataset is not None and dataset not in DATASET_NAMES:
        raise ValueError("Given dataset name does not exist: " + dataset)

    indicator_class = name_to_class(class_type="indicator", name=indicator_name)
    indicator = indicator_class(
        layer_name=layer_name, bpolys=bpolys, dataset=dataset, feature_id=feature_id
    )

    # Create indicator from scratch
    if bpolys is not None and dataset is None and feature_id is None:
        indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()

    # Create indicator by loading existing results from database
    # or in case it this does fail create indicator from scratch and
    # save results to database.
    elif dataset is not None and feature_id is not None:
        try:
            success = load_indicator_results(indicator)
        except UndefinedTable:
            success = False
        if not success:
            indicator.preprocess()
            indicator.calculate()
            indicator.create_figure()
            save_indicator_results(indicator)
    return indicator


def create_report(
    report_name: str,
    bpolys: FeatureCollection = None,
    dataset: str = None,
    feature_id: int = None,
) -> object:
    """Create a report.

    A Report is created by either calculaating each indicator
    from scratch and combine the results together or
    by fetching already calculated and combined reports from the geodatabase.

    Returns:
        Report object
    """
    report_class = name_to_class(class_type="report", name=report_name)
    report = report_class(bpolys=bpolys, dataset=dataset, feature_id=feature_id)
    report.set_indicator_layer()
    for indicator_name, layer_name in report.indicator_layer:
        indicator = create_indicator(
            indicator_name,
            layer_name,
            report.bpolys,
            report.dataset,
            report.feature_id,
        )
        report.indicators.append(indicator)
    report.combine_indicators()
    return report


# TODO: Generalize. This is a temporary solution.
def create_indicators_for_dataset(dataset_name):
    """Create indicators for all features of a dataset.

    Results are saved the database.
    """
    fids = get_fid_list(dataset_name)
    for feature_id in fids:
        for indicator_name, layer_name in (
            ("GhsPopComparison", "building_count"),
            ("MappingSaturation", "building_count"),
            ("MappingSaturation", "major_roads"),
            ("MappingSaturation", "amenities"),
            ("LastEdit", "major_roads"),
            ("LastEdit", "building_count"),
            ("LastEdit", "amenities"),
            ("PoiDensity", "poi"),
        ):
            try:
                create_indicator(
                    indicator_name,
                    layer_name,
                    dataset=dataset_name,
                    feature_id=feature_id,
                )
            # TODO: Those errors are raised during MappingCalculation creation.
            # Issue 72
            except (ValueError, TypeError) as error:
                logger.error(error)
                logger.error(
                    f"Error occurred during creation of indicator "
                    f"'{indicator_name}' for the dataset '{dataset_name}' "
                    f"and feature_id '{feature_id}'. "
                    f"Continue creation of the indicators for the other features."
                )
                continue
