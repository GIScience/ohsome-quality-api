import os

import geojson

from ohsome_quality_api.attributes.definitions import get_attribute
from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import Topic


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_topic_fixture(name: str) -> Topic:
    return get_topic_preset(name)


def get_attribute_fixture(a_key: str, topic_key: str) -> Attribute:
    return get_attribute(a_key, topic_key)
