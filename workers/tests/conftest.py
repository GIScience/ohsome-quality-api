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
from ohsome_quality_analyst.indicators.models import IndicatorMetadata

# from ohsome_quality_analyst.indicators import MappingSaturation
# from ohsome_quality_analyst.indicators.models import BaseIndicator as Indicator
from ohsome_quality_analyst.topics.models import TopicDefinition

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture(scope="class")
def topic_key_building_count() -> str:
    return "building_count"


@pytest.fixture(scope="class")
def topic_building_count(topic_key_building_count) -> TopicDefinition:
    return get_topic_definition(topic_key_building_count)


@pytest.fixture()
def topics_dict() -> dict[str, TopicDefinition]:
    return load_topic_definitions()


@pytest.fixture()
def topics_list(topics_dict) -> dict[str, TopicDefinition]:
    return topics_dict


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
def indicator_metadata_minimal() -> IndicatorMetadata:
    return get_metadata("indicators", "Minimal")


@pytest.fixture
def indicators_metadata() -> dict[str, IndicatorMetadata]:
    return load_metadata("indicators")
