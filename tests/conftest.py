import logging
import os

import geojson
import pytest
from geojson import Feature, FeatureCollection, Polygon

from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.definitions import (
    get_metadata,
    load_metadata,
)
from ohsome_quality_api.indicators.models import IndicatorMetadata
from ohsome_quality_api.projects.definitions import get_project, load_projects
from ohsome_quality_api.projects.models import Project
from ohsome_quality_api.quality_dimensions.definitions import (
    get_quality_dimension,
    load_quality_dimensions,
)
from ohsome_quality_api.quality_dimensions.models import QualityDimension
from ohsome_quality_api.reports.models import ReportMetadata
from ohsome_quality_api.topics.definitions import (
    get_topic_preset,
    load_topic_presets,
)
from ohsome_quality_api.topics.models import TopicDefinition

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

# TODO: Workaround to avoid cluttering of stdout because of
# https://github.com/pytest-dev/pytest/issues/5502
logger = logging.getLogger("rpy2")
logger.propagate = False


@pytest.fixture(scope="class")
def topic_key_minimal() -> str:
    return "minimal"


@pytest.fixture(scope="class")
def topic_key_building_count() -> str:
    return "building-count"


@pytest.fixture(scope="class")
def topic_minimal(topic_key_minimal) -> TopicDefinition:
    return get_topic_preset(topic_key_minimal)


@pytest.fixture(scope="class")
def topic_building_count(topic_key_building_count) -> TopicDefinition:
    return get_topic_preset(topic_key_building_count)


@pytest.fixture(scope="class")
def topic_building_area() -> TopicDefinition:
    return get_topic_preset("building-area")


@pytest.fixture(scope="class")
def topic_major_roads_length() -> TopicDefinition:
    return get_topic_preset("roads")


@pytest.fixture(scope="class")
def attribute_key_height() -> str:
    return "height"


@pytest.fixture(scope="class")
def metadata_topic_building_count(
    topic_key_building_count,
    topic_building_count,
) -> dict[str, TopicDefinition]:
    return {topic_key_building_count: topic_building_count}


@pytest.fixture()
def topic_definitions() -> dict[str, TopicDefinition]:
    return load_topic_presets()


@pytest.fixture(scope="class")
def quality_dimension_key_completeness() -> str:
    return "completeness"


@pytest.fixture(scope="class")
def quality_dimension_completeness(
    quality_dimension_key_completeness,
) -> QualityDimension:
    return get_quality_dimension(quality_dimension_key_completeness)


@pytest.fixture(scope="class")
def metadata_quality_dimension_completeness(
    quality_dimension_key_completeness,
    quality_dimension_completeness,
) -> dict[str, QualityDimension]:
    return {quality_dimension_key_completeness: quality_dimension_completeness}


@pytest.fixture()
def quality_dimensions() -> dict[str, QualityDimension]:
    return load_quality_dimensions()


@pytest.fixture(scope="class")
def project_key_core() -> str:
    return "core"


@pytest.fixture(scope="class")
def project_core(project_key_core) -> Project:
    return get_project(project_key_core)


@pytest.fixture(scope="class")
def metadata_project_core(project_key_core, project_core) -> dict[str, Project]:
    return {project_key_core: project_core}


@pytest.fixture()
def projects() -> dict[str, Project]:
    return load_projects()


@pytest.fixture(scope="class")
def attribute() -> Attribute:
    return Attribute(
        name="test attribute",
        description="super descriptive text",
        filter="(height=* or building:levels=*)",
    )


@pytest.fixture(scope="class")
def attribute_key() -> str:
    return ["height"]


@pytest.fixture(scope="class")
def attribute_key_multiple() -> str:
    return ["height", "house_number"]


@pytest.fixture(scope="class")
def feature_germany_heidelberg() -> Feature:
    path = os.path.join(
        FIXTURE_DIR,
        "feature-germany-heidelberg.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)


@pytest.fixture(scope="class")
def feature_germany_berlin() -> Feature:
    path = os.path.join(
        FIXTURE_DIR,
        "feature-germany-berlin-friedrichshain-kreuzberg.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)


@pytest.fixture(scope="class")
def feature_malta() -> Feature:
    path = os.path.join(
        FIXTURE_DIR,
        "feature-malta.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)


@pytest.fixture(scope="class")
def feature(feature_germany_heidelberg) -> Feature:
    return feature_germany_heidelberg


@pytest.fixture(scope="class")
def feature_collection_germany_heidelberg() -> FeatureCollection:
    # Single Feature
    path = os.path.join(
        FIXTURE_DIR,
        "feature-collection-germany-heidelberg.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)


@pytest.fixture(scope="class")
def bpolys(feature_collection_germany_heidelberg) -> FeatureCollection:
    return feature_collection_germany_heidelberg


@pytest.fixture(scope="class")
def feature_collection_heidelberg_bahnstadt_bergheim_weststadt() -> FeatureCollection:
    # Multiple Features
    path = os.path.join(
        FIXTURE_DIR,
        "feature-collection-heidelberg-bahnstadt-bergheim-weststadt.geojson",
    )
    with open(path, "r") as f:
        return geojson.load(f)


@pytest.fixture
def feature_collection_invalid() -> FeatureCollection:
    # Invalid Geometry
    return FeatureCollection(
        features=[
            Feature(
                geometry=Polygon(
                    [[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.0, 1.0)]]
                )
            )
        ]
    )


@pytest.fixture(params=["Point", "LineString", "Polygon"])
def geojson_unsupported_object_type(request):
    if request.param == "Feature":
        return Feature(geometry=geojson.utils.generate_random("Polygon"))
    return geojson.utils.generate_random(request.param)


@pytest.fixture(params=["Point", "LineString"])
def feature_collection_unsupported_geometry_type(request) -> FeatureCollection:
    # Invalid Geometry
    return FeatureCollection(
        features=[
            Feature(
                geometry=geojson.utils.generate_random(request.param),
            ),
        ]
    )


@pytest.fixture
def metadata_indicator_minimal() -> dict[str, IndicatorMetadata]:
    return {"minimal": get_metadata("indicators", "Minimal")}


@pytest.fixture
def indicators_metadata() -> dict[str, IndicatorMetadata]:
    return load_metadata("indicators")


@pytest.fixture
def metadata_report_minimal() -> dict[str, ReportMetadata]:
    return {"minimal": get_metadata("reports", "Minimal")}


@pytest.fixture
def reports_metadata() -> dict[str, ReportMetadata]:
    return load_metadata("reports")
