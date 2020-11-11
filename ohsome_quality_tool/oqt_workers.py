import ast

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


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable logging.")
def cli(verbose):
    if not verbose:
        logger.disabled = True
    else:
        logger.info("Logging enabled")


@cli.command("indicator")
@click.option(
    "--indicator",
    "-i",
    help="Compute the indicator with the given name.",
    type=str,
)
@click.option(
    "--indicators",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        "Derive multiple indicators. "
        "Provide indicator name strings as a list: "
        """'["indicator_a", "indicator_b"]'"""
    ),
)
@click.option(
    "infile",
    "-f",
    help="GeoJSON file for your area of interest.",
    type=str,
    required=True,
)
def derive_indicators(indicator, indicators, infile):
    """Derive one or multiple indicators for given geojson file."""
    if not indicator and not indicators:
        click.echo("Missing argument")
        return None
    elif not indicators:
        indicators = [indicator]

    with open(infile, "r") as file:
        bpolys = geojson.load(file)

    for i, indicator_name in enumerate(indicators):
        indicator = Indicators[indicator_name].constructor(bpolys=bpolys)
        indicator.run()


@cli.command("report")
@click.option(
    "--report",
    "-r",
    help="Compute the report with the given name.",
    type=str,
)
@click.option(
    "--reports",
    cls=PythonLiteralOption,
    default="[]",
    help=(
        "Derive multiple reports. "
        "Provide report name strings as a list: "
        """'["report_a", "report_b"]'"""
    ),
)
@click.option(
    "infile",
    "-f",
    help="GeoJSON file for your area of interest.",
    type=str,
    required=True,
)
def derive_reports(report, reports, infile):
    """Derive one or multiple reports for given geojson file."""
    if not report and not reports:
        click.echo("Missing argument")
        return None
    elif not reports:
        reports = [report]

    with open(infile, "r") as file:
        bpolys = geojson.load(file)

    for i, report_name in enumerate(reports):
        report = Reports[report_name].constructor(bpolys=bpolys)
        report.run()
