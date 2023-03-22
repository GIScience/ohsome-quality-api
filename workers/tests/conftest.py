import os

import geojson
import pytest
from geojson import Feature, FeatureCollection

from ohsome_quality_analyst.base.topic import BaseTopic as Layer
from ohsome_quality_analyst.definitions import get_topic_definition

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture(scope="class")
def topic_building_count() -> Layer:
    return get_topic_definition("building_count")


@pytest.fixture(scope="class")
def feature_germany_heidelberg() -> Feature:
    path = os.path.join(
        FIXTURE_DIR,
        "feature-germany-heidelberg.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)


@pytest.fixture(scope="class")
def feature_collection_germany_heidelberg_bahnstadt_bergheim() -> FeatureCollection:
    path = os.path.join(
        FIXTURE_DIR,
        "feature-collection-germany-heidelberg-bahnstadt-bergheim.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)
