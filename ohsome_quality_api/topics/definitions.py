import os
from enum import Enum

import yaml
from fastapi_i18n import _

from ohsome_quality_api.projects.definitions import ProjectEnum
from ohsome_quality_api.topics.models import TopicDefinition
from ohsome_quality_api.utils.helper import get_module_dir


def load_topic_presets() -> dict[str, TopicDefinition]:
    """Read ohsome API parameters of all topic from YAML file."""
    directory = get_module_dir("ohsome_quality_api.topics")
    file = os.path.join(directory, "presets.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    topics = {}
    for k, v in raw.items():
        v["filter"] = v.pop("filter")
        v["key"] = k
        topics[k] = TopicDefinition(**v)
    return topics


def get_topic_keys() -> list[str]:
    return [str(t) for t in load_topic_presets().keys()]


def get_topic_presets(project: ProjectEnum = None) -> dict[str, TopicDefinition]:
    topics = load_topic_presets()
    if project is not None:
        return {k: v for k, v in topics.items() if project in v.projects}
    else:
        return topics


def get_topic_preset(topic_key: str) -> TopicDefinition:
    """Get ohsome API parameters of a single topic based on topic key."""
    topics = load_topic_presets()
    try:
        return topics[topic_key]
    except KeyError as error:
        raise KeyError(
            _("Invalid topic key. Valid topic keys are: ") + str(topics.keys())
        ) from error


def get_valid_topics(indicator_name: str) -> tuple:
    """Get valid Indicator/Topic combination of an Indicator."""
    td = load_topic_presets()
    return tuple(topic for topic in td if indicator_name in td[topic].indicators)


TopicEnum = Enum("TopicEnum", {name: name for name in get_topic_keys()})
