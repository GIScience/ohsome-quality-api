import ast
import asyncio
import logging

import click
import geojson
import yaml

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.cli_opts import (
    dataset_name_opt,
    feature_id_opt,
    force_opt,
    indicator_name_opt,
    infile_opt,
    layer_name_opt,
    report_name_opt,
)
from ohsome_quality_analyst.utils.definitions import (
    DATASET_NAMES,
    configure_logging,
    load_layer_definitions,
    load_metadata,
)


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except ValueError as e:
            logging.exception(e)
            raise click.BadParameter(value)


def add_opts(options):
    """Adds options to cli."""

    def _add_opts(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_opts


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
    """List in the Geodatabase available datasets."""
    click.echo(DATASET_NAMES)


@cli.command("create-indicator")
@add_opts(indicator_name_opt)
@add_opts(layer_name_opt)
@add_opts(infile_opt)
@add_opts(dataset_name_opt)
@add_opts(feature_id_opt)
@add_opts(force_opt)
def create_indicator(
    indicator_name: str,
    infile: str,
    layer_name: str,
    feature_id: int,
    dataset_name: str,
    force: bool,
):
    """Create an Indicator and print results to stdout."""
    # TODO: replace this with a function that loads the file AND
    #    checks the validity of the geometries, e.g. enforce polygons etc.
    if force:
        click.echo(
            "The argument 'force' will update the indicator result in the database."
        )
        click.confirm("Do you want to continue?", abort=True)
    if infile:
        with open(infile, "r") as file:
            bpolys = geojson.load(file)
        if bpolys.is_valid is False:
            raise ValueError("Input geometry is not valid")
        for i in range(len(bpolys.features)):
            bpolys_subset = geojson.FeatureCollection([bpolys.features[i]])
            indicator = asyncio.run(
                oqt.create_indicator(
                    indicator_name=indicator_name,
                    bpolys=bpolys_subset,
                    layer_name=layer_name,
                    feature_id=feature_id,
                    dataset=dataset_name,
                    force=force,
                )
            )
            m = vars(indicator.metadata)
            r = vars(indicator.result)
            bpolys["features"][i]["properties"].update(m)
            bpolys["features"][i]["properties"].update(r)
            click.echo(indicator.metadata)
            click.echo(indicator.result)
        try:
            outputfile = infile[:-8] + "_%s.geojson" % indicator_name
            with open(outputfile, "w") as f:
                geojson.dump(bpolys, f)
        except Exception as err:
            logging.error(
                "could not write outputfile %s. Error: %s" % (outputfile, err)
            )
    else:
        bpolys = None
        indicator = asyncio.run(
            oqt.create_indicator(
                indicator_name=indicator_name,
                bpolys=bpolys,
                layer_name=layer_name,
                feature_id=feature_id,
                dataset=dataset_name,
                force=force,
            )
        )
        # TODO: Print out readable format.
        click.echo(indicator.metadata)
        click.echo(indicator.result)


@cli.command("create-report")
@add_opts(report_name_opt)
@add_opts(infile_opt)
@add_opts(dataset_name_opt)
@add_opts(feature_id_opt)
@add_opts(force_opt)
def create_report(
    report_name: str, infile: str, dataset_name: str, feature_id: int, force: bool
):
    """Create a Report and print results to stdout."""
    if infile:
        with open(infile, "r") as file:
            bpolys = geojson.load(file)
        if bpolys.is_valid is False:
            raise ValueError("Input geometry is not valid")
    else:
        bpolys = None
    report = asyncio.run(
        oqt.create_report(
            report_name=report_name,
            bpolys=bpolys,
            dataset=dataset_name,
            feature_id=feature_id,
            force=force,
        )
    )
    # TODO: Print out readable format.
    click.echo(report.metadata)
    click.echo(report.result)


# TODO: Dataset option is mandatory
@cli.command("create-all-indicators")
@add_opts(force_opt)
@click.option(
    "--dataset_name",
    "-d",
    required=True,
    type=click.Choice(
        DATASET_NAMES,
        case_sensitive=True,
    ),
    help=("Choose a dataset containing geometries."),
)
def create_all_indicators(dataset_name: str, force: bool):
    """Create all indicators for a specified dataset."""
    click.echo(
        "This command will calculate all indicators for the specified dataset "
        + "and may take a while to complete."
    )
    if force:
        click.echo(
            "The argument 'force' will update the indicator results in the database."
        )
    click.confirm("Do you want to continue?", abort=True)
    asyncio.run(oqt.create_all_indicators(dataset=dataset_name, force=force))


if __name__ == "__main__":
    cli()
