from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import Reports, get_indicators

INDICATORS: Dict = get_indicators()


def get_dynamic_indicator(indicator_name: str, bpolys: FeatureCollection):
    """Get indicator results for given geojson file.

    The results will be calculated dynamically,
    e.g. by querying the ohsome api.
    """
    indicator = INDICATORS[indicator_name](dynamic=True, bpolys=bpolys)
    result, metadata = indicator.get()
    return result, metadata


def get_static_indicator(indicator_name: str, dataset: str, feature_id: int):
    """Get indicator results for a pre-defined area.

    The results have been pre-processed and will be extracted from the geo database.
    """
    # TODO: adjust arguments dynamic and bpolys
    indicator = INDICATORS[indicator_name](
        dynamic=False, dataset=dataset, feature_id=feature_id
    )
    result, metadata = indicator.get()
    return result, metadata


def process_indicator(indicator_name: str, dataset: str, feature_id: int):
    """Process indicator and save results to geo database.

    The indicator(s) will be calculated for all geometries in the dataset.
    """
    # TODO: adjust arguments dynamic and bpolys

    indicator = INDICATORS[indicator_name](
        dynamic=False, dataset=dataset, feature_id=feature_id
    )
    indicator.run_processing()
    indicator.save_to_database()


def get_dynamic_report(report_name: str, bpolys: FeatureCollection):
    """Get report for given geojson file.

    The indicator results will be calculated dynamically,
    e.g. by querying the ohsome api.
    """

    result, indicators, metadata = (
        Reports[report_name].constructor(dynamic=True, bpolys=bpolys).get()
    )
    return result, indicators, metadata


def get_static_report(report_name: str, dataset: str, feature_id: int):
    """Get report with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    # TODO: adjust arguments bpolys
    report = Reports[report_name].constructor(
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
    report = Reports[report_name].constructor(
        dynamic=False, dataset=dataset, feature_id=feature_id
    )
    result, indicators, metadata = report.get()
    report.export_as_pdf(outfile=outfile)
