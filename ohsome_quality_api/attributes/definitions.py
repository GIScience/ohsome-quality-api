import os
from enum import Enum
from typing import List

import yaml

from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.topics.definitions import get_topic_preset, load_topic_presets
from ohsome_quality_api.utils.helper import get_module_dir


def is_ohsomedb_enabled() -> bool:
    ohsomedb_enabled = get_config_value("ohsomedb_enabled")
    if ohsomedb_enabled or ohsomedb_enabled in ("True", "true"):  # noqa: SIM103
        return True
    else:
        return False


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


def build_attribute_filter(
    attribute_filter: str | None,
    attribute_keys: list[str],
    topic_key: str,
):
    if is_ohsomedb_enabled():
        return build_attribute_filter_ohsomedb(
            attribute_filter,
            attribute_keys,
            topic_key,
        )
    else:
        return build_attribute_filter_ohsomeapi(
            attribute_filter,
            attribute_keys,
            topic_key,
        )


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


def build_attribute_filter_ohsomedb(
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


def build_attribute_filter_ohsomeapi(
    attribute_filter: str | None,
    attribute_keys: list[str] | None,
    topic_key: str,
) -> str:
    """Build attribute filter for ohsome API query."""
    attributes = get_attributes()
    try:
        if attribute_keys is not None:
            attribute_filter = get_topic_preset(topic_key).filter
            for attribute_key in attribute_keys:
                attribute_filter += (
                    " and (" + attributes[topic_key][attribute_key].filter + ")"
                )
            return attribute_filter
        elif attribute_filter is not None:
            return (
                get_topic_preset(topic_key).filter + " and (" + attribute_filter + ")"
            )
        else:
            raise ValueError("Attribute filter or keys has to be given.")
    except KeyError as error:
        raise KeyError("Invalid topic or attribute key(s).") from error


attribute_keys = {
    inner_key for outer_dict in load_attributes().values() for inner_key in outer_dict
}

AttributeEnum = Enum("AttributeEnum", {name: name for name in attribute_keys})
