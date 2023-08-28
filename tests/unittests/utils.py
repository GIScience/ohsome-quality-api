import os

import geojson

from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import TopicDefinition


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_topic_fixture(name: str) -> TopicDefinition:
    return get_topic_preset(name)
