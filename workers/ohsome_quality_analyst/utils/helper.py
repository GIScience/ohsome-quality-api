"""
Standalone helper functions.
"""

import datetime
import importlib
import logging
import os
import pathlib
import pkgutil
import re

import geojson


def name_to_class(class_type: str, name: str):
    """Convert class name of class type (indicator or report) to the class.

    Assumptions:
    - Class is named in Camel Case (E.g. GhsPopComparison).
    - Path to the module is in Snake Case (E.g. indicators.ghs_pop_comparison.indicator)
    """
    # Alternatives:
    # - Hard code import of classes
    # - Dynamically import all classes in package
    #     - https://julienharbulot.com/python-dynamical-import.html
    class_path = "ohsome_quality_analyst.{0}s.{1}.{2}".format(
        class_type,
        camel_to_snake(name),
        class_type,
    )
    return getattr(importlib.import_module(class_path), name)


def camel_to_snake(camel: str) -> str:
    """Converts Camel Case to Snake Case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()


def snake_to_lower_camel(snake: str) -> str:
    """Convertes Snake Case to Lower Camel Case"""
    parts = snake.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def name_to_lower_camel(name: str) -> str:
    """Convert name to Lower Camel Case"""
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    return snake_to_lower_camel(name)


def get_module_dir(module_name: str) -> str:
    """Get directory of module name."""
    module = pkgutil.get_loader(module_name)
    return os.path.dirname(module.get_filename())


def datetime_to_isostring_timestamp(time: datetime) -> str:
    """
    Checks for datetime objects and converts them to ISO 8601 format.

    Serves as function that gets called for objects that can’t otherwise be
    serialized by the `json` module.
    It should return a JSON encodable version of the object or raise a TypeError.
    https://docs.python.org/3/library/json.html#basic-usage
    """
    try:
        return time.isoformat()
    except AttributeError:
        raise TypeError


def load_infile(infilepath):
    """loads the input file as feature collection which will be used as input for
    indicator or report calculations"""
    infile = pathlib.Path(infilepath)
    with open(infile, "r") as file:
        feature_collection = geojson.load(file)
    if feature_collection.is_valid is False:
        raise ValueError("Input geometry is not valid")
    return feature_collection


def write_geojson(outfile, feature_collection):
    """Writes the Feature Collection to the disk at the specified directory. Creates
    the dir if it does not exist"""
    outfile = pathlib.Path(outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    with open(outfile, "w") as f:
        geojson.dump(feature_collection, f, default=datetime_to_isostring_timestamp)
        logging.info("Output file written:\t" + str(outfile))


def update_features_indicator(feature, indicator):
    """adds the indicator metadata, result and resultdata (if available) to the
    properties of a feature"""
    if indicator.data is not None:
        feature["properties"].update(indicator.data)
    feature["properties"].update(vars(indicator.metadata).copy())
    feature["properties"].update(vars(indicator.result).copy())
    return feature


def update_features_report(feature, report):
    """adds the report metadata and result to the properties of a feature"""
    feature["properties"].update(vars(report.metadata))
    feature["properties"].update(vars(report.result))
    return feature
