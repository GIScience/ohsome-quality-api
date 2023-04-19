import os

import geojson

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_geojson_fixture(filename):
    path = os.path.join(
        FIXTURE_DIR,
        filename,
    )
    with open(path, "r") as f:
        return geojson.load(f)
