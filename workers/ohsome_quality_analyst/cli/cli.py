import asyncio
import json
import logging

import click
import geojson
import yaml

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import (
    IndicatorBpolys,
    IndicatorDatabase,
    ReportBpolys,
    ReportDatabase,
)
from ohsome_quality_analyst.cli import options
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.definitions import (
    DATASETS,
    INDICATOR_LAYER,
    configure_logging,
    load_layer_definitions,
    load_metadata,
)
from ohsome_quality_analyst.utils.helper import json_serialize, write_geojson


def cli_option(option):
    """Adds options to cli."""

    def _cli_option(func):
        return option(func)

    return _cli_option


@click.group()
@click.version_option()
@click.option("--quiet", "-q", is_flag=True, help="Disable logging.")
def cli(quiet: bool):
    if not quiet:
        configure_logging()
        logging.info("Logging enabled")
        logging.debug("Debugging output enabled")


@cli.command("list-indicators")
def list_indicators():
    """List available indicators and their metadata."""
    metadata = load_metadata("indicators")
    metadata = yaml.dump(metadata, default_style="|")
    click.echo(metadata)


@cli.command("list-reports")
def list_reports():
    """List available reports and their metadata."""
    metadata = load_metadata("reports")
    metadata = yaml.dump(metadata, default_style="|")
    click.echo(metadata)


@cli.command("list-layers")
def list_layers():
    """List available layers and how they are defined (ohsome API parameters)."""
    layers = load_layer_definitions()
    layers = yaml.dump(layers, default_style="|")
    click.echo(layers)


@cli.command("list-datasets")
def list_datasets():
    """List available datasets."""
    click.echo(tuple(DATASETS.keys()))


@cli.command("list-fid-fields")
def list_fid_fields():
    """List available fid fields for each dataset."""
    for name, dataset in DATASETS.items():
        click.echo(name + ": ")
        click.echo("  - default: " + dataset["default"])
        click.echo("  - other: " + ", ".join(dataset.get("other", [])))


@cli.command("list-regions")
def get_available_regions():
    """List available regions."""
    regions = asyncio.run(db_client.get_regions())
    format_row = "{:>4}{:>20}"
    click.echo(format_row.format("fid", "name"))
    click.echo(format_row.format("---", "-" * 19))
    for region in sorted(regions, key=lambda k: k["ogc_fid"]):
        click.echo(format_row.format(region["ogc_fid"], region["name"]))


@cli.command("list-indicator-layer-combination")
def get_indicator_layer_combination():
    """List all possible indicator-layer-combinations."""
    for combination in INDICATOR_LAYER:
        click.echo(combination)


@cli.command("create-indicator")
@cli_option(options.indicator_name)
@cli_option(options.layer_name)
@cli_option(options.infile)
@cli_option(options.outfile)
@cli_option(options.dataset_name)
@cli_option(options.feature_id)
@cli_option(options.fid_field)
@cli_option(options.force)
def create_indicator(
    indicator_name: str,
    infile: str,
    outfile: str,
    layer_name: str,
    feature_id: str,
    dataset_name: str,
    fid_field: str,
    force: bool,
):
    """Create an Indicator.

    Output is a GeoJSON Feature or FeatureCollection with the indicator results.
    Output will be printed to stdout.
    Only if the `outfile` option is specified the output will be written to disk.
    """
    if force:
        click.echo(
            "The argument 'force' will update the indicator result in the database."
        )
        click.confirm("Do you want to continue?", abort=True)
    if infile is not None:
        with open(infile, "r") as file:
            bpolys = json.load(file)
        parameters = IndicatorBpolys(
            name=indicator_name,
            layerName=layer_name,
            bpolys=bpolys,
        )
    else:
        parameters = IndicatorDatabase(
            name=indicator_name,
            layerName=layer_name,
            dataset=dataset_name,
            featureId=feature_id,
            fidField=fid_field,
        )
    geojson_object = asyncio.run(oqt.create_indicator_as_geojson(parameters, force))
    if outfile:
        write_geojson(outfile, geojson_object)
    click.echo(geojson.dumps(geojson_object, default=json_serialize, allow_nan=True))


@cli.command("create-report")
@cli_option(options.report_name)
@cli_option(options.infile)
@cli_option(options.outfile)
@cli_option(options.dataset_name)
@cli_option(options.feature_id)
@cli_option(options.fid_field)
@cli_option(options.force)
def create_report(
    report_name: str,
    infile: str,
    outfile: str,
    dataset_name: str,
    feature_id: str,
    fid_field: str,
    force: bool,
):
    """Create a Report.

    Output is a GeoJSON Feature or FeatureCollection with the report/ indicator results.
    Output will be printed to stdout.
    Only if the `outfile` option is specified the output will be written to disk.
    """
    if force:
        click.echo(
            "The argument 'force' will update the indicator results in the database."
        )
        click.confirm("Do you want to continue?", abort=True)
    if infile is not None:
        with open(infile, "r") as file:
            bpolys = json.load(file)
        parameters = ReportBpolys(name=report_name, bpolys=bpolys)
    else:
        parameters = ReportDatabase(
            name=report_name,
            dataset=dataset_name,
            featureId=feature_id,
            fidField=fid_field,
        )
    geojson_object = asyncio.run(oqt.create_report_as_geojson(parameters, force))
    if outfile:
        write_geojson(outfile, geojson_object)
    click.echo(geojson.dumps(geojson_object, default=json_serialize, allow_nan=True))


@cli.command("create-all-indicators")
@cli_option(options.force)
def create_all_indicators(force: bool):
    """Create all indicators for all OQT regions."""
    click.echo(
        "This command will calculate all indicators for all OQT regions "
        + "and may take a while to complete."
    )
    if force:
        click.echo(
            "The argument 'force' will update the indicator results in the database."
        )
    click.confirm("Do you want to continue?", abort=True)
    asyncio.run(oqt.create_all_indicators(force=force))


if __name__ == "__main__":
    cli()
