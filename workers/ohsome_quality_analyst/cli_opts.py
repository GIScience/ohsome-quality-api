"""
Define Click command options to avoid redundancy.
"""

import click

from ohsome_quality_analyst.utils.definitions import (
    DATASET_NAMES,
    load_layer_definitions,
    load_metadata,
)

indicator_name_opt = [
    click.option(
        "--indicator-name",
        "-i",
        required=True,
        type=click.Choice(
            load_metadata("indicators").keys(),
            case_sensitive=True,
        ),
        help="Choose an indicator,valid indicators are specified in definitions.py .",
    )
]

report_name_opt = [
    click.option(
        "--report-name",
        "-r",
        required=True,
        type=click.Choice(
            load_metadata("reports").keys(),
            case_sensitive=True,
        ),
        help="Choose a report,valid reports are specified in definitions.py .",
    )
]

infile_opt = [
    click.option(
        "--infile",
        help="GeoJSON file for your area of interest.",
        type=str,
        default=None,
    )
]

outfile_opt = [
    click.option(
        "--outfile",
        help="GeoJSON file to be written with appended metadata and results.",
        type=str,
        default=None,
    )
]

dataset_name_opt = [
    click.option(
        "--dataset-name",
        "-d",
        type=click.Choice(
            DATASET_NAMES,
            case_sensitive=True,
        ),
        help=("Choose a dataset containing geometries."),
        default=None,
    )
]

layer_name_opt = [
    click.option(
        "--layer-name",
        "-l",
        required=True,
        type=click.Choice(
            list(load_layer_definitions().keys()),
            case_sensitive=True,
        ),
        help=(
            "Choose a layer. This defines which OSM features will be considered "
            + "in the quality analysis."
        ),
    )
]

feature_id_opt = [
    click.option(
        "--feature-id",
        "-f",
        type=int,
        help="Provide the feature id of your area of interest.",
        default=None,
    )
]

force_opt = [
    click.option(
        "--force",
        is_flag=True,
        help=(
            "Force recreation of indicator. "
            + "This will update the results of an indicator in the database."
        ),
    )
]
