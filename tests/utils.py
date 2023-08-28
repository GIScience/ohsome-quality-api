import json
import os

from geojson_pydantic import Feature, FeatureCollection

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_geojson_fixture(filename):
    path = os.path.join(
        FIXTURE_DIR,
        filename,
    )
    with open(path, "r") as f:
        gjson = json.load(f)
        if gjson["type"] == "FeatureCollection":
            return FeatureCollection(**gjson)
        else:
            return Feature(**gjson)
