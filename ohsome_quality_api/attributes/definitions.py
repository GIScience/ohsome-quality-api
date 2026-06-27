import os
from enum import Enum

import yaml

from ohsome_quality_api.attributes.models import Attribute
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


def build_attribute_title(
    attribute_title: str | None,
    attribute_keys: list[str] | None,
    topic_key: str,
) -> str:
    if attribute_keys is not None:
        return ", ".join(
            [get_attribute(topic_key, k).name.lower() for k in attribute_keys]
        )
    elif attribute_title is not None:
        return attribute_title
    else:
        raise ValueError("Attribute keys or title has to be given.")


def build_attribute_filter(
    attribute_filter: str | None,
    attribute_keys: list[str] | None,
    topic_key: str,
) -> str:
    """Build attribute filter for ohsomeDB query."""
    attributes = get_attributes()
    try:
        if attribute_keys is not None:
            attribute_filter = ""
            for i, attribute_key in enumerate(attribute_keys):
                if i == 0:
                    attribute_filter = (
                        "(" + attributes[topic_key][attribute_key].filter + ")"
                    )
                else:
                    attribute_filter += (
                        " and (" + attributes[topic_key][attribute_key].filter + ")"
                    )
            return attribute_filter
        elif attribute_filter is not None:
            return "(" + attribute_filter + ")"
        else:
            raise ValueError("Attribute filter or keys has to be given.")
    except KeyError as error:
        raise KeyError("Invalid topic or attribute key(s).") from error


attribute_keys = {
    inner_key for outer_dict in load_attributes().values() for inner_key in outer_dict
}

AttributeEnum = Enum("AttributeEnum", {name: name for name in attribute_keys})
