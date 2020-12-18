from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import (
    get_indicator_classes,
    get_report_classes,
    logger,
)
from ohsome_quality_tool.utils.geodatabase import (
    create_error_table,
    get_error_table_name,
    get_fid_list,
    insert_error,
)
from ohsome_quality_tool.utils.layers import get_all_layer_definitions

INDICATOR_CLASSES: Dict = get_indicator_classes()
REPORT_CLASSES: Dict = get_report_classes()


def process_indicator(
    dataset: str, indicator_name: str, layer_name: str, only_missing_ids: bool = False
):
    """Processes indicator and save results in geo database."""
    # TODO: we need to define here which layer should be processed
    if only_missing_ids is False:
        fids = get_fid_list(dataset)
    else:
        fids = get_fid_list(get_error_table_name(dataset, indicator_name))

    layer = get_all_layer_definitions()[layer_name]

    create_error_table(dataset, indicator_name, layer.name)
    for feature_id in fids:
        try:
            indicator = INDICATOR_CLASSES[indicator_name](
                dynamic=False, dataset=dataset, feature_id=feature_id, layer=layer
            )
            result = indicator.run_processing()
            indicator.save_to_database(result)
        except Exception as E:
            insert_error(dataset, indicator_name, layer.name, feature_id, E)
            logger.info(
                (
                    f"caught Exception while processing {indicator_name} "
                    f"{E} "
                    f"for feature {feature_id} of {dataset}."
                )
            )


def get_dynamic_indicator(indicator_name: str, bpolys: FeatureCollection):
    """Get indicator results for given geojson file.

    The results will be calculated dynamically,
    e.g. by querying the ohsome api.
    """
    indicator = INDICATOR_CLASSES[indicator_name](dynamic=True, bpolys=bpolys)
    result, metadata = indicator.get()
    return result, metadata


def get_static_indicator(indicator_name: str, dataset: str, feature_id: int):
    """Get indicator results for a pre-defined area.

    The results have been pre-processed and will be extracted from the geo database.
    """
    # TODO: adjust arguments dynamic and bpolys
    indicator = INDICATOR_CLASSES[indicator_name](
        dynamic=False, dataset=dataset, feature_id=feature_id
    )
    result, metadata = indicator.get()
    return result, metadata


def get_dynamic_report(report_name: str, bpolys: FeatureCollection):
    """Get report for given geojson file.

    The indicator results will be calculated dynamically,
    e.g. by querying the ohsome api.
    """

    result, indicators, metadata = REPORT_CLASSES[report_name](
        dynamic=True, bpolys=bpolys
    ).get()
    return result, indicators, metadata


def get_static_report(report_name: str, dataset: str, feature_id: int):
    """Get report with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    # TODO: adjust arguments bpolys
    report = REPORT_CLASSES[report_name](
        dynamic=False, dataset=dataset, feature_id=feature_id
    )
    result, indicators, metadata = report.get()
    return result, indicators, metadata


def get_static_report_pdf(
    report_name: str, dataset: str, feature_id: int, outfile: str
):
    """Get report as PDF with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    # TODO: adjust arguments bpolys
    report = REPORT_CLASSES[report_name](
        dynamic=False, dataset=dataset, feature_id=feature_id
    )
    result, indicators, metadata = report.get()
    report.export_as_pdf(outfile=outfile)
