import asyncio
import logging

import click

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.config import configure_logging, get_config_value
from ohsome_quality_analyst.definitions import get_topic_keys, load_metadata


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


@cli.command("create-all-indicators")
@click.option(
    "--dataset-name",
    "-d",
    required=True,
    type=click.Choice(
        get_config_value("datasets").keys(),
        case_sensitive=True,
    ),
    help=("Choose a dataset containing geometries."),
)
@click.option(
    "--indicator-name",
    "-i",
    type=click.Choice(
        load_metadata("indicators").keys(),
        case_sensitive=True,
    ),
    help="Choose an indicator,valid indicators are specified in definitions.py .",
    default=None,
)
@click.option(
    "--topic-key",
    "-l",
    type=click.Choice(
        get_topic_keys(),
        case_sensitive=True,
    ),
    help=(
        "Choose a topic. This defines which OSM features will be considered "
        "in the quality analysis."
    ),
    default=None,
)
@click.option(
    "--force",
    is_flag=True,
    help=(
        "Force recreation of indicator. "
        "This will update the results of an indicator in the database."
    ),
)
def create_all_indicators(
    dataset_name: str,
    indicator_name: str,
    topic_key: str,
    force: bool,
):
    """Create all Indicators for all features of the given dataset.

    The default is to create all Indicator/Topic combinations for all features of the
    given dataset. This can be restricted to one Indicator type and/or one Topic
    definition by providing the corresponding options.
    """
    click.echo(
        "This command will calculate all indicators for all features of the given "
        + "dataset. This may take a while to complete."
    )
    if force:
        click.echo(
            "The argument 'force' will overwrite existing indicator results in the "
            + "database."
        )
    click.confirm("Do you want to continue?", abort=True)
    asyncio.run(
        oqt.create_all_indicators(
            dataset_name,
            indicator_name=indicator_name,
            topic_key=topic_key,
            force=force,
        )
    )


if __name__ == "__main__":
    cli()
