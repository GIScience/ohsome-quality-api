import os

import geojson
from dacite import from_dict

from ohsome_quality_analyst.base.layer import LayerDefinition
from ohsome_quality_analyst.utils.definitions import get_layer_definition


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_layer_fixture(name: str) -> LayerDefinition:
    return from_dict(data_class=LayerDefinition, data=get_layer_definition(name))
