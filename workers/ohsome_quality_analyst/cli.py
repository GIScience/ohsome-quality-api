import asyncio
import logging

import click
import geojson
import yaml
from geojson import FeatureCollection

from ohsome_quality_analyst import cli_opts, oqt
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.definitions import (
    DATASETS,
    configure_logging,
    load_layer_definitions,
    load_metadata,
)
from ohsome_quality_analyst.utils.helper import (
    datetime_to_isostring_timestamp,
    loads_geojson,
    write_geojson,
)


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
    """List available layers and how they are definied (ohsome API parameters)."""
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
    regions = asyncio.run(db_client.get_available_regions())
    click.echo(regions)


@cli.command("create-indicator")
@cli_option(cli_opts.indicator_name)
@cli_option(cli_opts.layer_name)
@cli_option(cli_opts.infile)
@cli_option(cli_opts.outfile)
@cli_option(cli_opts.dataset_name)
@cli_option(cli_opts.feature_id)
@cli_option(cli_opts.fid_field)
@cli_option(cli_opts.force)
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
            bpolys = file.read()
        features = []
        for feature in loads_geojson(bpolys):
            indicator = asyncio.run(
                oqt.create_indicator(
                    indicator_name,
                    layer_name,
                    feature=feature,
                    feature_id=feature_id,
                    dataset=dataset_name,
                    fid_field=fid_field,
                    force=force,
                )
            )
            features.append(indicator.as_feature())
        geojson_object = FeatureCollection(features=features)
    else:
        # When using a dataset and FID as input
        indicator = asyncio.run(
            oqt.create_indicator(
                indicator_name,
                layer_name,
                feature=None,
                feature_id=feature_id,
                dataset=dataset_name,
                fid_field=fid_field,
                force=force,
            )
        )
        geojson_object = indicator.as_feature()
    if outfile:
        write_geojson(outfile, geojson_object)
    click.echo(geojson.dumps(geojson_object, default=datetime_to_isostring_timestamp))


@cli.command("create-report")
@cli_option(cli_opts.report_name)
@cli_option(cli_opts.infile)
@cli_option(cli_opts.outfile)
@cli_option(cli_opts.dataset_name)
@cli_option(cli_opts.feature_id)
@cli_option(cli_opts.fid_field)
@cli_option(cli_opts.force)
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
            bpolys = file.read()
        features = []
        for feature in loads_geojson(bpolys):
            report = asyncio.run(
                oqt.create_report(
                    report_name,
                    feature=feature,
                    dataset=dataset_name,
                    feature_id=feature_id,
                    fid_field=fid_field,
                    force=force,
                )
            )
            features.append(report.as_feature())
        geojson_object = FeatureCollection(features=features)
    else:
        # When using a dataset and FID as input
        report = asyncio.run(
            oqt.create_report(
                report_name,
                feature=None,
                dataset=dataset_name,
                feature_id=feature_id,
                fid_field=fid_field,
                force=force,
            )
        )
        geojson_object = report.as_feature()
    if outfile:
        write_geojson(outfile, geojson_object)
    click.echo(geojson.dumps(geojson_object, default=datetime_to_isostring_timestamp))


@cli.command("create-all-indicators")
@cli_option(cli_opts.force)
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
