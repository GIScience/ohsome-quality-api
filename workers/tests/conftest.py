import os

import geojson
import pytest
from geojson import Feature, FeatureCollection

from ohsome_quality_analyst.definitions import (
    get_metadata,
    get_topic_definition,
    load_metadata,
    load_topic_definitions,
)
from ohsome_quality_analyst.indicators.models import Metadata

# from ohsome_quality_analyst.indicators import MappingSaturation
# from ohsome_quality_analyst.indicators.models import BaseIndicator as Indicator
from ohsome_quality_analyst.topics.models import BaseTopic as Topic

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture(scope="class")
def topic_key_building_count() -> str:
    return "building_count"


@pytest.fixture(scope="class")
def topic_building_count(topic_key_building_count) -> Topic:
    return get_topic_definition(topic_key_building_count)


@pytest.fixture()
def topics() -> list[Topic]:
    return list(load_topic_definitions().values())


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


@pytest.fixture
def indicator_metadata_minimal() -> Metadata:
    return get_metadata("indicators", "Minimal")


@pytest.fixture
def indicators_metadata() -> list[Metadata]:
    return list(load_metadata("indicators").values())


# TODO
# @pytest.fixture()
# def indicator_mapping_saturation(
#     topic_key_building_count, feature_germany_heidelberg
# ) -> Indicator:
#     return MappingSaturation(
#         topic=topic_key_building_count,
#         feature=feature_germany_heidelberg,
#     )
