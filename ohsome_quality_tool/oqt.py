import ast
from typing import List

import click
import geojson

from ohsome_quality_tool.utils.definitions import Indicators, Reports, logger


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            logger.exception(e)
            raise click.BadParameter(value)


def add_options(options):
    """Functions adds options to cli."""

    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


_indicator_option = [
    click.option(
        "--indicator_name",
        "-i",
        required=True,
        type=click.Choice(
            list(Indicators.__members__),
            case_sensitive=True,
        ),
        help="Choose an indicator,valid indicators are specified in definitions.py .",
    )
]

_report_option = [
    click.option(
        "--report_name",
        "-r",
        required=True,
        type=click.Choice(
            list(Reports.__members__),
            case_sensitive=True,
        ),
        help="Choose a report,valid reports are specified in definitions.py .",
    )
]

_infile_option = [
    click.option(
        "--infile",
        help="GeoJSON file for your area of interest.",
        type=str,
        required=True,
    )
]

_table_option = [
    click.option(
        "--table",
        required=True,
        type=str,
        help="""Choose a table containing geometries,
            valid area tables are specified in definitions.py .""",
    )
]

_area_filter_option = [
    click.option(
        "--area_filter",
        required=True,
        type=str,
        help="""Choose a area filter,
            valid area filters are specified in definitions.py .""",
    )
]


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable logging.")
def cli(verbose):
    if not verbose:
        logger.disabled = True
    else:
        logger.info("Logging enabled")


@cli.command("get-dynamic-indicator")
@add_options(_indicator_option)
@add_options(_infile_option)
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


@cli.command("get-static-indicator")
@add_options(_indicator_option)
@add_options(_area_filter_option)
def get_static_indicator(indicator_name: str, area_filter: List[str]):
    """Get indicator results for a pre-defined area.

    The results have been pre-processed and will be extracted from the geo database.
    """
    # TODO: adjust arguments dynamic and bpolys
    indicator = Indicators[indicator_name].constructor(dynamic=False, bpolys="")
    indicator.get()


@cli.command("process-indicator")
@add_options(_indicator_option)
@add_options(_table_option)
def process_indicator(indicator_name: str, table: str):
    """Process indicator and save results to geo database.

    The indicator(s) will be calculated for all geometries in the table.
    """
    # TODO: adjust arguments dynamic and bpolys

    indicator = Indicators[indicator_name].constructor(dynamic=False, bpolys="")
    indicator.run_processing()
    indicator.save_to_database()


@cli.command("get-dynamic-report")
@add_options(_report_option)
@add_options(_infile_option)
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
    report = Reports[report_name].constructor(bpolys=bpolys)
    report.run()


@cli.command("get-static-report")
@add_options(_report_option)
@add_options(_area_filter_option)
def get_static_report(report_name: str, area_filter: str):
    """Get report with indicator results for a pre-defined area.

    The indicator results have been pre-processed and
    will be extracted from the geo database."""
    # TODO: adjust arguments bpolys
    report = Reports[report_name].constructor(bpolys="")
    report.run()
