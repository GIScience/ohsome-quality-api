import json
import os

from geojson_pydantic import FeatureCollection

from ohsome_quality_api.api.request_models import FeatureWithOptionalProperties
from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import TopicDefinition


def get_geojson_fixture(name) -> FeatureWithOptionalProperties | FeatureCollection:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        geo_json = json.load(f)

        if geo_json["type"] == "Feature":
            return FeatureWithOptionalProperties(**geo_json)
        else:
            return FeatureCollection[FeatureWithOptionalProperties](**geo_json)


def get_topic_fixture(name: str) -> TopicDefinition:
    return get_topic_preset(name)
