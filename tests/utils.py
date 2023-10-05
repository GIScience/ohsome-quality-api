import json
import os

from ohsome_quality_api.api.request_models import Feature, FeatureCollection

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_geojson_fixture(filename):
    path = os.path.join(
        FIXTURE_DIR,
        filename,
    )
    with open(path, "r") as f:
        gjson = json.load(f)
        if gjson["type"] == "FeatureCollection":
            return FeatureCollection[Feature](**gjson)
        else:
            return Feature(**gjson)
