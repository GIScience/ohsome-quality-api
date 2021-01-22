import importlib
import os
import pkgutil
import re


def name_to_class(class_name: str):
    """Convert class name of indicator to the class.

    Assumptions:
    - Class is named in Camel Case (E.g. GhsPopComparison).
    - Path to the module is in Snake Case (E.g. indicators.ghs_pop_comparison.indicator)
    """
    # Alternatives:
    # - Hard code import of classes
    # - Dynamically import all classes in package
    #     - https://julienharbulot.com/python-dynamical-import.html

    class_path = "ohsome_quality_tool.indicators.{0}.indicator".format(
        camel_to_snake(class_name)
    )
    return getattr(importlib.import_module(class_path), class_name)


def camel_to_snake(string: str) -> str:
    """Converts Camel Case to Snake Case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def get_module_dir(module_name: str) -> str:
    """Get directory of module name."""
    module = pkgutil.get_loader(module_name)
    return os.path.dirname(module.get_filename())
