import json
import os

from geojson_pydantic import Feature, FeatureCollection

from ohsome_quality_analyst.topics.definitions import get_topic_preset
from ohsome_quality_analyst.topics.models import TopicDefinition


def get_geojson_fixture(name) -> Feature | FeatureCollection:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        geo_json = json.load(f)

        if geo_json["type"] == "Feature":
            return Feature(**geo_json)
        else:
            return FeatureCollection(**geo_json)


def get_topic_fixture(name: str) -> TopicDefinition:
    return get_topic_preset(name)
