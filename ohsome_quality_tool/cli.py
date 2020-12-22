import ast

import click
import geojson

from ohsome_quality_tool import oqt
from ohsome_quality_tool.utils.definitions import (
    DATASET_NAMES,
    get_indicator_classes,
    get_report_classes,
    logger,
)
from ohsome_quality_tool.utils.layers import get_all_layer_definitions


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
            get_indicator_classes().keys(),
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
            get_report_classes().keys(),
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
            DATASET_NAMES,
            case_sensitive=True,
        ),
        help="""Choose a dataset containing geometries,
            valid area datasets are specified in definitions.py .""",
    )
]

_layer_name_option = [
    click.option(
        "--layer_name",
        required=True,
        type=click.Choice(
            list(get_all_layer_definitions().keys()),
            case_sensitive=True,
        ),
        help=(
            "Choose a layer. This defines which OSM features will be considered "
            "in the quality analysis."
        ),
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
@add_options(_layer_name_option)
def get_dynamic_indicator(indicator_name: str, infile: str, layer_name: str):
    # TODO: replace this with a function that loads the file AND
    #    checks the validity of the geometries, e.g. enforce polygons etc.
    with open(infile, "r") as file:
        bpolys = geojson.load(file)
    result, metadata = oqt.get_dynamic_indicator(
        indicator_name=indicator_name, bpolys=bpolys, layer_name=layer_name
    )
    print(result)
    print(metadata)
    return result, metadata


@cli.command("get-static-indicator")
@add_options(_indicator_option)
@add_options(_dataset_option)
@add_options(_feature_id_option)
@add_options(_layer_name_option)
def get_static_indicator(
    indicator_name: str, dataset: str, feature_id: int, layer_name: str
):
    result, metadata = oqt.get_static_indicator(
        indicator_name=indicator_name,
        dataset=dataset,
        feature_id=feature_id,
        layer_name=layer_name,
    )
    return result, metadata


@cli.command("process-indicator")
@add_options(_indicator_option)
@add_options(_dataset_option)
@add_options(_layer_name_option)
@add_options(
    [
        click.option(
            "--missing_fids",
            is_flag=True,
            help="Flag wether only should only missing FIDs be processed",
        )
    ]
)
def process_indicator(
    indicator_name: str, dataset: str, layer_name: str, missing_fids: bool
):
    oqt.process_indicator(
        indicator_name=indicator_name,
        dataset=dataset,
        layer_name=layer_name,
        only_missing_ids=missing_fids,
    )


@cli.command("process-all-indicators")
@add_options(_dataset_option)
def process_all_indicators(dataset: str):
    # TODO: here we need to consider the different layers as well
    #   this means that we might need to process an indicator
    #   several times, e.g. for BUILDING_COUNT_LAYER and then also
    #   for the MAJOR_ROADS_LAYER
    #   Ideally we would check the reports for this
    #   In the reports we will find information on which indicators
    #   should be processed for which layers
    indicators = [
        ("ghspop-comparison", "building-count"),
        ("mapping-saturation", "building-count"),
        ("mapping-saturation", "major-roads"),
        ("mapping-saturation", "amenities"),
        ("last-edit", "major-roads"),
        ("last-edit", "building-count"),
        ("last-edit", "amenities"),
        ("poi-density", "points-of-interests"),
    ]
    for indicator_name, layer_name in indicators:
        oqt.process_indicator(
            indicator_name=indicator_name,
            dataset=dataset,
            layer_name=layer_name,
            only_missing_ids=False,
        )


@cli.command("get-dynamic-report")
@add_options(_report_option)
@add_options(_infile_option)
def get_dynamic_report(report_name: str, infile: str):
    with open(infile, "r") as file:
        bpolys = geojson.load(file)
    result, indicators, metadata = oqt.get_dynamic_report(
        report_name=report_name, bpolys=bpolys
    )
    return result, indicators, metadata


@cli.command("get-static-report")
@add_options(_report_option)
@add_options(_dataset_option)
@add_options(_feature_id_option)
def get_static_report(report_name: str, dataset: str, feature_id: int):
    result, indicators, metadata = oqt.get_static_report(
        report_name=report_name, dataset=dataset, feature_id=feature_id
    )
    return result, indicators, metadata


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
