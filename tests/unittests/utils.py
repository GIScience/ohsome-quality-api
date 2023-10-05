import json
import os

from ohsome_quality_api.api.request_models import (
    Feature,
    FeatureCollection,
)
from ohsome_quality_api.attributes.definitions import get_attribute
from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import TopicDefinition


def get_geojson_fixture(
    name,
) -> Feature | FeatureCollection:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        geo_json = json.load(f)

        if geo_json["type"] == "Feature":
            return Feature(**geo_json)
        else:
            return FeatureCollection[Feature](**geo_json)


def get_topic_fixture(name: str) -> TopicDefinition:
    return get_topic_preset(name)


def get_attribute_fixture(a_key: str, topic_key: str) -> Attribute:
    return get_attribute(a_key, topic_key)
