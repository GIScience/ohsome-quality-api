"""
Controller for the creation of Indicators and Reports.
Functions are triggert by the CLI and API.
"""

from geojson import FeatureCollection

from ohsome_quality_tool.geodatabase.client import (
    create_error_table,
    get_error_table_name,
    get_fid_list,
    insert_error,
)
from ohsome_quality_tool.utils.definitions import logger
from ohsome_quality_tool.utils.helper import name_to_class


def create_indicator(
    indicator_name: str,
    layer_name: str,
    bpolys: FeatureCollection = None,
    dataset: str = None,
    feature_id: int = None,
):
    """Create an indicator.

    An indicator is created by either calculating the indicator
    for a geometry or by fetching already calculated from the geodatabase.

    Returns:
        Indicator object
    """

    indicator_class = name_to_class(class_type="indicator", name=indicator_name)
    if bpolys:
        indicator = indicator_class(layer_name=layer_name, bpolys=bpolys)
        indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()
    elif dataset and feature_id:
        indicator = indicator_class(
            layer_name=layer_name, dataset=dataset, feature_id=feature_id
        )
        indicator.get_from_database()
    else:
        raise ValueError(
            "Provide either a bounding polygone "
            + "or dataset name and feature id as parameter."
        )
    return indicator


def create_report(
    report_name: str, bpolys: FeatureCollection, dataset: str, feature_id: int
):
    """Create a report.

    A Report is created by either calculaating each indicator
    from scratch and combine the results together or
    by fetching already calculated and combined reports from the geodatabase.

    Returns:
        Report object
    """
    report_class = name_to_class(class_type="report", name=report_name)
    if bpolys:
        report = report_class(bpolys=bpolys, dataset=dataset, feature_id=feature_id)
    elif dataset and feature_id:
        report = None
        pass
    else:
        raise ValueError(
            "Provide either a bounding polygone "
            + "or dataset name and feature id as parameter."
        )
    return report


def process_indicator(
    dataset: str, indicator_name: str, layer_name: str, only_missing_ids: bool = False
):
    """Processes indicator and save results in geo database."""
    # TODO: we need to define here which layer should be processed
    if only_missing_ids is False:
        fids = get_fid_list(dataset)
    else:
        fids = get_fid_list(get_error_table_name(dataset, indicator_name))

    create_error_table(dataset, indicator_name, layer_name)
    for feature_id in fids:
        try:
            indicator_class = name_to_class(class_type="indicator", name=indicator_name)
            indicator = indicator_class(
                dynamic=False,
                dataset=dataset,
                feature_id=feature_id,
                layer_name=layer_name,
            )
            indicator.preprocess()
            indicator.calculate()
            indicator.create_figure()
            indicator.save_to_database()
        except Exception as E:
            insert_error(dataset, indicator_name, layer_name, feature_id, E)
            logger.info(
                (
                    f"caught Exception while processing {indicator_name} "
                    f"{E} "
                    f"for feature {feature_id} of {dataset}."
                )
            )


def get_dynamic_indicator(
    indicator_name: str, bpolys: FeatureCollection, layer_name: str
):
    raise NotImplementedError("Use create_indicator() instead")


def get_static_indicator(
    indicator_name: str, dataset: str, feature_id: int, layer_name: str
):
    raise NotImplementedError("Use create_indicator() instead")


def get_dynamic_report(report_name: str, bpolys: FeatureCollection):
    raise NotImplementedError("Use create_report() instead")


def get_static_report(report_name: str, dataset: str, feature_id: int):
    raise NotImplementedError("Use create_report() instead")


def get_static_report_pdf(
    report_name: str, dataset: str, feature_id: int, outfile: str
):
    """Get report as PDF with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    raise NotImplementedError()
