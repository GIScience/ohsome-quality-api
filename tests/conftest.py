import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
import geojson
import pytest
from _pytest.monkeypatch import MonkeyPatch
from geojson import Feature, FeatureCollection, Polygon

from ohsome_quality_api.attributes.models import Attribute
from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.indicators.currentness.indicator import Bin
from ohsome_quality_api.indicators.definitions import (
    get_indicator,
    get_indicator_metadata,
)
from ohsome_quality_api.indicators.models import IndicatorMetadata
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

FIXTURE_DIR = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"))

# TODO: Workaround to avoid cluttering of stdout because of
# https://github.com/pytest-dev/pytest/issues/5502
logger = logging.getLogger("rpy2")
logger.propagate = False


# TODO: remove once ohsomedb has been replaced by ohsome-api
@pytest.fixture(autouse=True)
def get_connection(monkeypatch):
    @asynccontextmanager
    async def get_connection_(database="oqapidb"):
        match database:
            case "oqapidb":
                dsn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
                    host=get_config_value("postgres_host"),
                    port=get_config_value("postgres_port"),
                    database=get_config_value("postgres_db"),
                    user=get_config_value("postgres_user"),
                    password=get_config_value("postgres_password"),
                )
            case "ohsomedb":
                dsn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
                    host=get_config_value("ohsomedb_host"),
                    port=get_config_value("ohsomedb_port"),
                    database=get_config_value("ohsomedb_db"),
                    user=get_config_value("ohsomedb_user"),
                    password=get_config_value("ohsomedb_password"),
                )
        connection = await asyncpg.connect(dsn)
        try:
            if database == "ohsomedb":
                sql = 'set search_path to "global_2026-04-27",public'
                await connection.execute(sql)
            yield connection
        finally:
            await connection.close()

    monkeypatch.setattr(
        "ohsome_quality_api.geodatabase.client.get_connection",
        get_connection_,
    )


@pytest.fixture(scope="class")
def topic_key_building_count() -> str:
    return "building-count"


@pytest.fixture(scope="class")
def topic_key_building_area() -> str:
    return "building-building-area"


@pytest.fixture(scope="class")
def topic_roads() -> Topic:
    return get_topic_preset("roads")


@pytest.fixture(scope="class")
def topic_roads_all_highways() -> Topic:
    return get_topic_preset("roads-all-highways")


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
def topic_custom() -> Topic:
    topic = get_topic_preset("custom-topic")
    topic.filter = "amenity=fountain and geometry:point"
    topic.name = "Fountains"
    return topic


@pytest.fixture(scope="class")
def attribute_key_height() -> list[str]:
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
def metadata_indicator_currentness() -> dict[str, IndicatorMetadata]:
    return {"currentness": get_indicator("currentness")}


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


@pytest.fixture(scope="class")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()
