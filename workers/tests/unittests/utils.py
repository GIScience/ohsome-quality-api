import os

import geojson

from ohsome_quality_analyst.base.topic import TopicDefinition
from ohsome_quality_analyst.definitions import get_topic_definition


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_layer_fixture(name: str) -> TopicDefinition:
    return get_topic_definition(name)
