import os

import geojson

from ohsome_quality_analyst.topics.definitions import get_topic_definition
from ohsome_quality_analyst.topics.models import TopicDefinition


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_topic_fixture(name: str) -> TopicDefinition:
    return get_topic_definition(name)
