import geojson

from ohsome_quality_tool.utils.definitions import Indicators, Reports


def get_dynamic_indicator(indicator_name: str, infile: str):
    """Get indicator results for given geojson file.

    The results will be calculated dynamically,
    e.g. by querying the ohsome api.
    """
    # TODO: replace this with a function that loads the file AND
    #    checks the validity of the geometries, e.g. enforce polygons etc.
    with open(infile, "r") as file:
        bpolys = geojson.load(file)

    indicator = Indicators[indicator_name].constructor(dynamic=True, bpolys=bpolys)
    indicator.get()
    print(f"results: {indicator.results}")
    return indicator.results


def get_static_indicator(indicator_name: str, table: str, feature_id: int):
    """Get indicator results for a pre-defined area.

    The results have been pre-processed and will be extracted from the geo database.
    """
    # TODO: adjust arguments dynamic and bpolys
    indicator = Indicators[indicator_name].constructor(
        dynamic=False, table=table, feature_id=feature_id
    )
    indicator.get()
    print(f"results: {indicator.results}")
    return indicator.results


def process_indicator(indicator_name: str, table: str, feature_id: int):
    """Process indicator and save results to geo database.

    The indicator(s) will be calculated for all geometries in the table.
    """
    # TODO: adjust arguments dynamic and bpolys

    indicator = Indicators[indicator_name].constructor(
        dynamic=False, table=table, feature_id=feature_id
    )
    indicator.run_processing()
    indicator.save_to_database()


def get_dynamic_report(report_name: str, infile: str):
    """Get report for given geojson file.

    The indicator results will be calculated dynamically,
    e.g. by querying the ohsome api.
    """
    # TODO: replace this with a function that loads the file AND
    #    checks the validity of the geometries, e.g. enforce polygons etc.
    with open(infile, "r") as file:
        bpolys = geojson.load(file)

    # TODO: add argument dynamic
    report = Reports[report_name].constructor(dynamic=True, bpolys=bpolys)
    report.get()
    print(f"results: {report.results}")
    return report.results


def get_static_report(report_name: str, table: str, feature_id: int):
    """Get report with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    # TODO: adjust arguments bpolys
    report = Reports[report_name].constructor(
        dynamic=False, table=table, feature_id=feature_id
    )
    report.get()
    print(f"results: {report.results}")
    return report.results


def get_static_report_pdf(report_name: str, table: str, feature_id: int, outfile: str):
    """Get report as PDF with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    # TODO: adjust arguments bpolys
    report = Reports[report_name].constructor(
        dynamic=False, table=table, feature_id=feature_id
    )
    report.get()
    report.export_as_pdf(outfile=outfile)
