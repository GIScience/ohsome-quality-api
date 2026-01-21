from dataclasses import asdict
from datetime import datetime

import asyncpg_recorder
import pytest
from approvaltests import Options, verify_as_json
from pydantic_core import to_jsonable_python
from pytest_approval import verify, verify_json

from ohsome_quality_api.indicators.roads_thematic_accuracy.indicator import (
    RoadsThematicAccuracy,
)
from tests.approvaltests_namers import PytestNamer
from tests.approvaltests_reporters import PlotlyDiffReporter


def mock_response(
    total_dlm=0,
    present_in_both=0,
    only_dlm=0,
    only_osm=0,
    missing_both=0,
    present_in_both_agree=0,
    present_in_both_not_agree=0,
    not_matched=0,
):
    return [
        {
            "total_dlm": total_dlm,
            "present_in_both": present_in_both,
            "only_dlm": only_dlm,
            "only_osm": only_osm,
            "missing_both": missing_both,
            "present_in_both_agree": present_in_both_agree,
            "present_in_both_not_agree": present_in_both_not_agree,
            "not_matched": not_matched,
        }
    ]


@pytest.fixture
def mock_attribute():
    return "surface"


@asyncpg_recorder.use_cassette
@pytest.mark.parametrize(
    "attribute",
    (
        "surface",
        "oneway",
        "lanes",
        "name",
        "width",
        None,
    ),
)
@pytest.mark.asyncio
async def test_preprocess(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )
    assert indicator.attribute == attribute
    await indicator.preprocess()
    assert indicator.matched_data is not None
    verify_json(asdict(indicator.matched_data))
    assert isinstance(indicator.result.timestamp_osm, datetime)
    assert isinstance(indicator.timestamp_dlm, datetime)


@asyncpg_recorder.use_cassette
@pytest.mark.parametrize(
    "attribute",
    (
        "surface",
        "oneway",
        "lanes",
        "name",
        "width",
        None,
    ),
)
@pytest.mark.asyncio
async def test_calculate(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    # non-quality indicator does not have result value
    assert indicator.result.value is None
    verify(indicator.result.description)


@pytest.mark.asyncio
async def test_calculate_no_data(feature, topic_roads, mock_attribute, monkeypatch):
    async def mock_fetch(*args, **kwargs):
        return mock_response()

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.roads_thematic_accuracy.indicator.client.fetch",
        mock_fetch,
    )
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=mock_attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    verify(indicator.result.description)
    indicator.create_figure()  # should raise no error
    verify_as_json(
        to_jsonable_python(indicator.result.figure),
        options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
    )


@pytest.mark.asyncio
async def test_calculate_no_shared_attribute(
    feature, topic_roads, mock_attribute, monkeypatch
):
    async def mock_fetch(*args, **kwargs):
        return mock_response(total_dlm=10, only_dlm=4, only_osm=5, missing_both=1)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.roads_thematic_accuracy.indicator.client.fetch",
        mock_fetch,
    )
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=mock_attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    verify(indicator.result.description)
    verify_as_json(
        to_jsonable_python(indicator.result.figure),
        options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
    )


@asyncpg_recorder.use_cassette
@pytest.mark.parametrize(
    "attribute",
    (
        "surface",
        "oneway",
        "lanes",
        "name",
        "width",
        None,
    ),
)
@pytest.mark.asyncio
async def test_create_figure(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    verify_as_json(
        to_jsonable_python(indicator.result.figure),
        options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
    )


@asyncpg_recorder.use_cassette
@pytest.mark.asyncio
async def test_coverage(feature, topic_roads):
    indicator = RoadsThematicAccuracy(feature=feature, topic=topic_roads)

    result = await indicator.coverage()
    assert result[0].is_valid

    result = await indicator.coverage(inverse=True)
    assert result[0].is_valid
