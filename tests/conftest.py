import json
import logging
import os
from pathlib import Path
from typing import List

import geojson
import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi_i18n.main import Translator, translator
from geojson import Feature, FeatureCollection, Polygon

from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.indicators.currentness.indicator import Bin
from ohsome_quality_api.indicators.definitions import (
    get_indicator,
    get_indicator_metadata,
)
from ohsome_quality_api.indicators.models import IndicatorMetadata
from ohsome_quality_api.projects.definitions import get_project, load_projects
from ohsome_quality_api.projects.models import Project
from ohsome_quality_api.quality_dimensions.definitions import (
    get_quality_dimension,
    load_quality_dimensions,
)
from ohsome_quality_api.quality_dimensions.models import QualityDimension
from ohsome_quality_api.topics.definitions import (
    get_topic_preset,
    load_topic_presets,
)
from ohsome_quality_api.topics.models import Topic
from ohsome_quality_api.utils.helper import get_project_root

FIXTURE_DIR = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"))

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
def topic_roads() -> Topic:
    return get_topic_preset("roads")


@pytest.fixture(scope="class")
def topic_minimal(topic_key_minimal) -> Topic:
    return get_topic_preset(topic_key_minimal)


@pytest.fixture(scope="class")
def topic_building_count(topic_key_building_count) -> Topic:
    return get_topic_preset(topic_key_building_count)


@pytest.fixture(scope="class")
def topic_building_area() -> Topic:
    return get_topic_preset("building-area")


@pytest.fixture(scope="class")
def topic_major_roads_length() -> Topic:
    return get_topic_preset("roads")


@pytest.fixture(scope="class")
def attribute_key_height() -> List[str]:
    return ["height"]


@pytest.fixture(scope="class")
def metadata_topic_building_count(
    topic_key_building_count,
    topic_building_count,
) -> dict[str, Topic]:
    return {topic_key_building_count: topic_building_count}


@pytest.fixture()
def topic_definitions() -> dict[str, Topic]:
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
def attribute_key() -> list[str]:
    return ["height"]


@pytest.fixture(scope="class")
def attribute_key_multiple() -> list[str]:
    return ["height", "house-number"]


@pytest.fixture
def attribute_filter() -> str:
    """Custom attribute filter."""
    return "height=* or building:levels=*"


@pytest.fixture
def attribute_title() -> str:
    """Attributes title belonging to custom attribute filter (`attribute_filter)`."""
    return "Height"


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
    return {"minimal": get_indicator("minimal")}


@pytest.fixture
def indicators_metadata() -> dict[str, IndicatorMetadata]:
    return get_indicator_metadata()


@pytest.fixture
def feature_land_cover():
    gj_dict = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [8.63552791262136, 49.711771844660191],
                    [8.57181432038835, 49.710072815533977],
                    [8.545479368932039, 49.624271844660186],
                    [8.685649271844662, 49.642111650485433],
                    [8.685649271844662, 49.642111650485433],
                    [8.685649271844662, 49.642111650485433],
                    [8.63552791262136, 49.711771844660191],
                ]
            ],
        },
    }

    gj = json.dumps(gj_dict)

    return geojson.loads(gj)


@pytest.fixture
def topic_land_cover() -> Topic:
    return get_topic_preset("land-cover")


@pytest.fixture
def bin_total_factory():
    def _factory(contrib_abs):
        return Bin(contrib_abs, [], [])

    return _factory


@pytest.fixture
def locale_de(monkeypatch):
    monkeypatch.setenv(
        "FASTAPI_I18N__LOCALE_DIR",
        os.path.join(get_project_root(), "ohsome_quality_api/locale"),
    )
    token = translator.set(Translator(locale="de"))
    yield
    translator.reset(token)


@pytest.fixture(scope="class")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="class")
def locale_de_class(monkeysession):
    monkeysession.setenv(
        "FASTAPI_I18N__LOCALE_DIR",
        os.path.join(get_project_root(), "ohsome_quality_api/locale"),
    )
    token = translator.set(Translator(locale="de"))
    yield
    translator.reset(token)
