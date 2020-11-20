import ast

import click

from ohsome_quality_tool import oqt
from ohsome_quality_tool.utils.definitions import DATASETS, Indicators, Reports, logger


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

_outfile_option = [
    click.option(
        "--outfile",
        help="PDF file for your report.",
        type=str,
        required=True,
    )
]

_dataset_option = [
    click.option(
        "--dataset",
        required=True,
        type=click.Choice(
            DATASETS,
            case_sensitive=True,
        ),
        help="""Choose a dataset containing geometries,
            valid area datasets are specified in definitions.py .""",
    )
]

# TODO: define and double check expected data type here
_feature_id_option = [
    click.option(
        "--feature_id",
        required=True,
        type=str,
        help="""Provide the feature id of your area of interest.""",
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
    results = oqt.get_dynamic_indicator(indicator_name=indicator_name, infile=infile)
    return results


@cli.command("get-static-indicator")
@add_options(_indicator_option)
@add_options(_dataset_option)
@add_options(_feature_id_option)
def get_static_indicator(indicator_name: str, dataset: str, feature_id: int):
    results = oqt.get_static_indicator(
        indicator_name=indicator_name, dataset=dataset, feature_id=feature_id
    )
    return results


@cli.command("process-indicator")
@add_options(_indicator_option)
@add_options(_dataset_option)
@add_options(_feature_id_option)
def process_indicator(indicator_name: str, dataset: str, feature_id: int):
    oqt.process_indicator(
        indicator_name=indicator_name, dataset=dataset, feature_id=feature_id
    )


@cli.command("get-dynamic-report")
@add_options(_report_option)
@add_options(_infile_option)
def get_dynamic_report(report_name: str, infile: str):
    results = oqt.get_dynamic_report(report_name=report_name, infile=infile)
    return results


@cli.command("get-static-report")
@add_options(_report_option)
@add_options(_dataset_option)
@add_options(_feature_id_option)
def get_static_report(report_name: str, dataset: str, feature_id: int):
    results = oqt.get_static_report(
        report_name=report_name, dataset=dataset, feature_id=feature_id
    )
    return results


@cli.command("get-static-report-pdf")
@add_options(_report_option)
@add_options(_dataset_option)
@add_options(_feature_id_option)
@add_options(_outfile_option)
def get_static_report_pdf(
    report_name: str, dataset: str, feature_id: int, outfile: str
):
    oqt.get_static_report_pdf(
        report_name=report_name, dataset=dataset, feature_id=feature_id, outfile=outfile
    )
