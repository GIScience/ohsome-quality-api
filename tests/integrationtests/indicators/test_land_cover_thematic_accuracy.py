import json

import geojson
import pytest
from approvaltests import Options, verify, verify_as_json
from pydantic_core import to_jsonable_python

from ohsome_quality_api.api.request_models import CorineLandCoverClass
from ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator import (
    LandCoverThematicAccuracy,
)
from tests.approvaltests_namers import PytestNamer
from tests.approvaltests_reporters import PlotlyDiffReporter
from tests.conftest import FIXTURE_DIR


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


@pytest.fixture
def mock_db_fetch_no_data(monkeypatch):
    async def fetch(*_):
        return []

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.client.fetch",
        fetch,
    )


@pytest.fixture
def mock_cov(monkeypatch):
    async def fake_coverage(cls, inverse=False):
        return 1

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.get_covered_area",
        fake_coverage,
    )


@pytest.fixture
def mock_low_cov(monkeypatch):
    async def fake_coverage(cls, inverse=False):
        return 0.3

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_thematic_accuracy.indicator.get_covered_area",
        fake_coverage,
    )


# TODO: Support singe corine class


@pytest.mark.asyncio
async def test_preprocess_multi_class(
    feature_land_cover,
    topic_land_cover,
    mock_db_fetch,
    mock_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover, topic=topic_land_cover
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
        strict=False,
    ):
        assert isinstance(area, float)
        assert isinstance(clc_class_corine, str)
        assert isinstance(clc_class_corine, str)
    assert indicator.result.timestamp_osm is not None
    assert indicator.coverage_percent == 1


@pytest.mark.asyncio
async def test_preprocess_single_class(
    feature_land_cover,
    topic_land_cover,
    corine_class,
    mock_db_fetch_single_class,
    mock_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover,
        topic=topic_land_cover,
        corine_land_cover_class=corine_class,
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
        strict=False,
    ):
        assert isinstance(area, float)
        assert isinstance(clc_class_corine, str)
        assert isinstance(clc_class_corine, str)
    assert indicator.result.timestamp_osm is not None
    assert indicator.coverage_percent == 1


@pytest.mark.asyncio
async def test_calculate_no_data(
    feature_malta,
    topic_land_cover,
    corine_class,
    mock_db_fetch_no_data,
    mock_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_malta,
        topic=topic_land_cover,
        corine_land_cover_class=corine_class,
    )
    await indicator.preprocess()
    assert indicator.areas == []
    indicator.calculate()
    assert indicator.result.label == "undefined"
    assert indicator.result.value is None
    verify(indicator.result.description, namer=PytestNamer())
    indicator.create_figure()  # should raise no error


@pytest.mark.asyncio
async def test_calculate_multi_class(
    feature_land_cover,
    topic_land_cover,
    mock_db_fetch,
    mock_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover, topic=topic_land_cover
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.f1_score is not None
    assert indicator.result.value is not None
    assert indicator.result.class_ == 3
    assert indicator.result.label == "yellow"
    verify(indicator.result.description, namer=PytestNamer(postfix="description"))
    # verify(indicator.report, namer=PytestNamer(postfix="report"))


@pytest.mark.asyncio
async def test_calculate_low_coverage(
    feature_land_cover,
    topic_land_cover,
    mock_db_fetch,
    mock_low_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover, topic=topic_land_cover
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.f1_score is not None
    assert indicator.result.value is not None
    assert indicator.result.class_ == 3
    assert indicator.result.label == "yellow"
    verify(indicator.result.description, namer=PytestNamer(postfix="description"))


@pytest.mark.asyncio
async def test_calculate_single_class(
    feature_land_cover,
    topic_land_cover,
    corine_class,
    mock_db_fetch_single_class,
    mock_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover,
        topic=topic_land_cover,
        corine_land_cover_class=corine_class,
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.confusion_matrix_normalized is not None
    assert indicator.f1_score is not None
    assert indicator.result.value is not None
    assert indicator.result.class_ == 1
    assert indicator.result.label == "red"
    verify(indicator.result.description, namer=PytestNamer(postfix="description"))
    # verify(indicator.report, namer=PytestNamer(postfix="report"))


@pytest.mark.asyncio
async def test_figure_multi_class(
    feature_land_cover, topic_land_cover, mock_db_fetch, mock_cov
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover,
        topic=topic_land_cover,
    )
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
    feature_land_cover,
    topic_land_cover,
    corine_class,
    mock_db_fetch_single_class,
    mock_cov,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover,
        topic=topic_land_cover,
        corine_land_cover_class=corine_class,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert isinstance(indicator.result.figure, dict)
    verify_as_json(
        to_jsonable_python(indicator.result.figure),
        options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
    )


@pytest.mark.asyncio
@pytest.mark.skip()
async def test_coverage(
    feature_land_cover,
    topic_land_cover,
):
    indicator = LandCoverThematicAccuracy(
        feature=feature_land_cover,
        topic=topic_land_cover,
    )

    result = await indicator.coverage()
    geojson_object = geojson.loads(result[0])
    assert geojson_object.is_valid

    result = await indicator.coverage(inverse=True)
    geojson_object = geojson.loads(result[0])
    assert geojson_object.is_valid
