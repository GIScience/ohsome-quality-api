import os

import yaml

from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.utils.helper import get_module_dir


def load_attributes() -> dict[str, dict[str, Attribute]]:
    """Read definitions of attributes.
    Returns:
        A dict with all attributes included.
    """
    directory = get_module_dir("ohsome_quality_api.attributes")
    file = os.path.join(directory, "attributes.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    attributes = {}
    for k, v in raw.items():
        attributes[k] = {}
        for sub_k, sub_v in v.items():
            attributes[k][sub_k] = Attribute(**sub_v)
    return attributes


def get_attributes() -> dict[str, dict[str, Attribute]]:
    return load_attributes()


def get_attribute(topic_key, a_key: str | None) -> Attribute:
    attributes = get_attributes()
    try:
        # TODO: Workaround to be able to display indicator in dashboard.
        # Remove if dashboard handles attribution key selection.
        if a_key is None:
            return next(iter(attributes[topic_key].values()))
        return attributes[topic_key][a_key]
    except KeyError as error:
        raise KeyError("Invalid topic or attribute key.") from error
