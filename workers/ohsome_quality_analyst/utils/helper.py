"""
Standalone helper functions.
"""

import importlib
import os
import pkgutil
import re


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
