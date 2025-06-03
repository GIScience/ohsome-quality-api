import json

import pytest
from approvaltests import Options, verify, verify_as_json
from pydantic_core import to_jsonable_python

from ohsome_quality_api.api.request_models import CorineLandCoverClass
from ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator import (
    LandCoverThematicAccuracy,
)
from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import TopicDefinition
from tests.approvaltests_namers import PytestNamer
from tests.approvaltests_reporters import PlotlyDiffReporter
from tests.conftest import FIXTURE_DIR


@pytest.fixture
def feature():
    return {
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


@pytest.fixture
def topic() -> TopicDefinition:
    return get_topic_preset("land-cover")


@pytest.fixture
def corine_class() -> CorineLandCoverClass:
    return CorineLandCoverClass.AGRICULTURAL_AREAS_3


@pytest.fixture
def mock_db_fetch(monkeypatch):
    async def fetch(*_):
        with open(
            FIXTURE_DIR / "land-cover-thematic-accuracy-db-fetch-results.json", "r"
        ) as file:
            return json.load(file)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.client.fetch",
        fetch,
    )


@pytest.fixture
def mock_db_fetch_single_class(monkeypatch):
    async def fetch(*_):
        with open(
            FIXTURE_DIR
            / "land-cover-thematic-accuracy-single-class-db-fetch-results.json",
            "r",
        ) as file:
            return json.load(file)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.client.fetch",
        fetch,
    )


# TODO: Support singe corine class


@pytest.mark.asyncio
async def test_preprocess_multi_class(feature, topic, mock_db_fetch):
    indicator = LandCoverThematicAccuracy(feature=feature, topic=topic)
    await indicator.preprocess()
    assert isinstance(indicator.areas, list)
    assert isinstance(indicator.clc_classes_corine, list)
    assert isinstance(indicator.clc_classes_osm, list)
    assert len(indicator.areas) > 0
    assert len(indicator.clc_classes_corine) > 0
    assert len(indicator.clc_classes_osm) > 0
    for area, clc_class_corine, clc_class_corine in zip(
        indicator.areas,
        indicator.clc_classes_corine,
        indicator.clc_classes_osm,
    ):
        assert isinstance(area, float)
        assert isinstance(clc_class_corine, str)
        assert isinstance(clc_class_corine, str)
    assert indicator.result.timestamp_osm is not None


@pytest.mark.asyncio
async def test_preprocess_single_class(
    feature, topic, corine_class, mock_db_fetch_single_class
):
    indicator = LandCoverThematicAccuracy(
        feature=feature, topic=topic, corine_land_cover_class=corine_class
    )
    await indicator.preprocess()
    assert isinstance(indicator.areas, list)
    assert isinstance(indicator.clc_classes_corine, list)
    assert isinstance(indicator.clc_classes_osm, list)
    assert len(indicator.areas) > 0
    assert len(indicator.clc_classes_corine) > 0
    assert len(indicator.clc_classes_osm) > 0
    for area, clc_class_corine, clc_class_corine in zip(
        indicator.areas,
        indicator.clc_classes_corine,
        indicator.clc_classes_osm,
    ):
        assert isinstance(area, float)
        assert isinstance(clc_class_corine, str)
        assert isinstance(clc_class_corine, str)
    assert indicator.result.timestamp_osm is not None


@pytest.mark.asyncio
async def test_calculate_multi_class(feature, topic, mock_db_fetch):
    indicator = LandCoverThematicAccuracy(feature=feature, topic=topic)
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.confusion_matrix is not None
    assert indicator.f1_score is not None
    assert indicator.result.value is not None
    assert indicator.result.class_ == 3
    assert indicator.result.label == "yellow"
    verify(indicator.result.description, namer=PytestNamer(postfix="description"))
    verify(indicator.report, namer=PytestNamer(postfix="report"))


@pytest.mark.asyncio
async def test_calculate_single_class(
    feature, topic, corine_class, mock_db_fetch_single_class
):
    indicator = LandCoverThematicAccuracy(
        feature=feature, topic=topic, corine_land_cover_class=corine_class
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.confusion_matrix is not None
    assert indicator.f1_score is not None
    assert indicator.result.value is not None
    assert indicator.result.class_ == 1
    assert indicator.result.label == "red"
    verify(indicator.result.description, namer=PytestNamer(postfix="description"))
    verify(indicator.report, namer=PytestNamer(postfix="report"))


@pytest.mark.asyncio
async def test_figure_multi_class(feature, topic, mock_db_fetch):
    indicator = LandCoverThematicAccuracy(feature=feature, topic=topic)
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert isinstance(indicator.result.figure, dict)
    verify_as_json(
        to_jsonable_python(indicator.result.figure),
        options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
    )


@pytest.mark.asyncio
async def test_figure_single_class(
    feature, topic, corine_class, mock_db_fetch_single_class
):
    indicator = LandCoverThematicAccuracy(
        feature=feature, topic=topic, corine_land_cover_class=corine_class
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert isinstance(indicator.result.figure, dict)
    verify_as_json(
        to_jsonable_python(indicator.result.figure),
        options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
    )
