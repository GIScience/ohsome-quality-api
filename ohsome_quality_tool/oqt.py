from typing import Dict

from geojson import FeatureCollection

from ohsome_quality_tool.utils.definitions import (
    get_indicator_classes,
    get_report_classes,
    logger
)
from ohsome_quality_tool.utils.geodatabase import (
    get_fid_list,
    create_error_table,
    get_bpolys_from_db,
    save_indicator_results_to_db,
    insert_error,
    )
INDICATOR_CLASSES: Dict = get_indicator_classes()
REPORT_CLASSES: Dict = get_report_classes()

    
def process_indicator(dataset, indicator):
    """Processes an Indicator for a given dataset in the Database
    
    
    The results will be stored in the database"""
    
    fids = get_fid_list(dataset)
    create_error_table(dataset, indicator)
    
    for feature_id in fids:
        try:       
            bpolys = get_bpolys_from_db(dataset, feature_id)
            results = get_dynamic_indicator(indicator, bpolys)
            save_indicator_results_to_db(dataset, feature_id, indicator, results)
        except Exception as E:
            insert_error(dataset, indicator, feature_id, E)
            logger.info(f"caught Exception{E} while processing {indicator} for feature {feature_id} of {dataset}.")

def process_missing(dataset:str, indicator:str):
    """Processes the missing FIDs for a given dataset / indicator
    
    
    The results will be stored in the database"""
    fids = get_fid_list(f"{dataset}_{indicator}_errors")
    create_error_table(dataset, indicator)
    
    for feature_id in fids:
        try:       
            bpolys = get_bpolys_from_db(dataset, feature_id)
            results = get_dynamic_indicator(indicator, bpolys)
            save_indicator_results_to_db(dataset, feature_id, indicator, results)
        except Exception as E:
            insert_error(dataset, indicator, feature_id, E)
            logger.info(f"caught Exception{E} while processing {indicator} for feature {feature_id} of {dataset}.")
            
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
