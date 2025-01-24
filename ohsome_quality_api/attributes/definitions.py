import os
from enum import Enum
from functools import singledispatch
from typing import List

import yaml

from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.topics.definitions import get_topic_preset, load_topic_presets
from ohsome_quality_api.utils.helper import get_module_dir


def load_attributes() -> dict[str, dict[str, Attribute]]:
    """Read attributes from YAML file."""
    directory = get_module_dir("ohsome_quality_api.attributes")
    file = os.path.join(directory, "attributes.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    attributes = {}
    for topic_key, value in raw.items():
        attributes[topic_key] = {}
        for attribute_key, value_ in value.items():
            attributes[topic_key][attribute_key] = Attribute(**value_)
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
        raise KeyError("Invalid topic or attribute key(s).") from error


# TODO: Remove since it is the same as above?
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


@singledispatch
def build_attribute_filter(attributes: str | list, topic_key: str, trino: bool) -> str:
    raise NotImplementedError


@build_attribute_filter.register
def _(
    attributes: list,
    topic_key: str,
    trino: bool = False,
) -> str:
    """Build attribute filter from attributes keys."""
    if trino:
        filter = get_topic_preset(topic_key).sql_filter
    else:
        filter = get_topic_preset(topic_key).filter

    all_attributes = get_attributes()
    for key in attributes:
        if trino:
            filter += " AND (" + all_attributes[topic_key][key].filter_sql + ")"
        else:
            filter += " and (" + all_attributes[topic_key][key].filter + ")"

    return filter


@build_attribute_filter.register
def _(
    attributes: str,
    topic_key: str,
    trino: bool = False,
) -> str:
    """Build attribute filter from user given attribute filter."""
    if trino:
        topic_filter = get_topic_preset(topic_key).sql_filter
        filter = topic_filter + " AND (" + attributes + ")"
    else:
        topic_filter = get_topic_preset(topic_key).filter
        filter = topic_filter + " and (" + attributes + ")"
    return filter


attribute_keys = {
    inner_key
    for outer_dict in load_attributes().values()
    for inner_key in outer_dict.keys()
}

AttributeEnum = Enum("AttributeEnum", {name: name for name in attribute_keys})
