import os

import yaml

from ohsome_quality_analyst.attributes.models import Attribute
from ohsome_quality_analyst.utils.helper import get_module_dir


def load_attributes() -> dict[str, dict[str, Attribute]]:
    """Read definitions of attributes.

    Returns:
        A dict with all attributes included.
    """
    directory = get_module_dir("ohsome_quality_analyst.attributes")
    file = os.path.join(directory, "attributes.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    attributes = {}
    for k, v in raw.items():
        attributes[k] = {}
        for subK, subV in v.items():
            attributes[k][subK] = Attribute(**subV)
    return attributes


def get_attributes() -> dict[str, dict[str, Attribute]]:
    return load_attributes()


def get_attribute(topic_key, a_key: str) -> Attribute:
    attributes = get_attributes()
    try:
        return attributes[topic_key][a_key]
    except KeyError as error:
        raise KeyError("Invalid topic or attribute key.") from error
