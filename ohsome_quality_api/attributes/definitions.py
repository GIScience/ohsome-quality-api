import os
from typing import List

import yaml
from topics.definitions import get_topic_preset, load_topic_presets

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


def build_attribute_filter(attribute_key: List[str], topic_key: str) -> str:
    """Build attribute filter for ohsome API query."""
    attributes = get_attributes()
    try:
        if isinstance(attribute_key, str):
            return (
                get_topic_preset(topic_key).filter
                + " and "
                + attributes[topic_key][attribute_key].filter
            )
        else:
            attribute_filter = get_topic_preset(topic_key).filter
            for key in attribute_key:
                attribute_filter += " and " + attributes[topic_key][key].filter
            return attribute_filter
    except KeyError as error:
        raise KeyError("Invalid topic or attribute key(s).") from error


def get_attribute(topic_key, a_key: str | None) -> Attribute:
    attributes = get_attributes()
    try:
        # TODO: Workaround to be able to display indicator in dashboard.
        # Remove if dashboard handles attribution key selection.
        if a_key is None:
            return next(iter(attributes[topic_key].values()))
        return attributes[topic_key][a_key]
    except KeyError as error:
        raise KeyError("Invalid topic or attribute key(s).") from error


def get_attribute_preset(topic_key: str) -> List[Attribute]:
    """Get ohsome API parameters of a list of Attributes based on topic key."""
    attributes = load_attributes()
    try:
        return attributes[topic_key]
    except KeyError as error:
        topics = load_topic_presets()
        raise KeyError(
            "Invalid topic key. Valid topic keys are: " + str(topics.keys())
        ) from error
