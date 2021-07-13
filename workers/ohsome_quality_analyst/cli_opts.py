"""
Define Click command options to avoid redundancy.
"""

import click

from ohsome_quality_analyst.utils.definitions import (
    DATASETS,
    load_layer_definitions,
    load_metadata,
)

indicator_name = click.option(
    "--indicator-name",
    "-i",
    required=True,
    type=click.Choice(
        load_metadata("indicators").keys(),
        case_sensitive=True,
    ),
    help="Choose an indicator,valid indicators are specified in definitions.py .",
)

report_name = click.option(
    "--report-name",
    "-r",
    required=True,
    type=click.Choice(
        load_metadata("reports").keys(),
        case_sensitive=True,
    ),
    help="Choose a report,valid reports are specified in definitions.py .",
)

infile = click.option(
    "--infile",
    help=(
        "Path to a GeoJSON file. " "Geometry has to be of type Polygon or MultiPolygon."
    ),
    type=click.Path(resolve_path=True),
    default=None,
)

outfile = click.option(
    "--outfile",
    help=(
        "Path to a GeoJSON file. "
        "Path and file will be created if it does not exists."
    ),
    type=click.Path(resolve_path=True),
    default=None,
)

dataset_name = click.option(
    "--dataset-name",
    "-d",
    type=click.Choice(
        DATASETS.keys(),
        case_sensitive=True,
    ),
    help=("Choose a dataset containing geometries."),
    default=None,
)

layer_name = click.option(
    "--layer-name",
    "-l",
    required=True,
    type=click.Choice(
        list(load_layer_definitions().keys()),
        case_sensitive=True,
    ),
    help=(
        "Choose a layer. This defines which OSM features will be considered "
        "in the quality analysis."
    ),
)

feature_id = click.option(
    "--feature-id",
    "-f",
    type=str,
    help="Provide the feature id of your area of interest.",
    default=None,
)

fid_field = click.option(
    "--fid-field",
    type=str,
    help=(
        "Provide the feature id field of the dataset. "
        "Use command list-fid-fields to view available "
        "fid fields for each dataset"
    ),
    default=None,
)

force = click.option(
    "--force",
    is_flag=True,
    help=(
        "Force recreation of indicator. "
        "This will update the results of an indicator in the database."
    ),
)
