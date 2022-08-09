import os

import geojson

from ohsome_quality_analyst.base.layer import LayerDefinition
from ohsome_quality_analyst.definitions import get_layer_definition


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_layer_fixture(name: str) -> LayerDefinition:
    return get_layer_definition(name)
