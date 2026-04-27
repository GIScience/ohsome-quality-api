import asyncpg_recorder
import pytest
from pytest_approval.main import verify, verify_plotly

from ohsome_quality_api.indicators.land_cover_completeness.indicator import (
    LandCoverCompleteness,
)
from tests.integrationtests.utils import oqapi_vcr


@pytest.fixture(autouse=True, params=[True, False])
def ohsomedb_feature_flag(request, monkeypatch):
    monkeypatch.setattr(
        "ohsome_quality_api.indicators.land_cover_completeness.indicator.is_ohsomedb_enabled",
        lambda: request.param,
    )


@pytest.mark.asyncio
@asyncpg_recorder.use_cassette
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_preprocess(
    topic_land_cover,
    feature_germany_heidelberg,
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_germany_heidelberg,
    )
    await indicator.preprocess()
    assert indicator.osm_area_ratio in (0.95454328, 0.8178082640896415)
    assert verify(indicator.result.timestamp_osm.isoformat())


@pytest.mark.asyncio
@asyncpg_recorder.use_cassette
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_calculate(
    topic_land_cover,
    feature_germany_heidelberg,
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_germany_heidelberg,
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.result.value in (0.95, 0.82)
    assert indicator.result.class_ in (5, 3)
    assert indicator.result.label in ("green", "yellow")
    assert verify(indicator.result.description)


@pytest.mark.asyncio
@asyncpg_recorder.use_cassette
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_calculate_above_100(
    topic_land_cover,
    feature_germany_heidelberg,
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_germany_heidelberg,
    )
    await indicator.preprocess()
    indicator.osm_area_ratio = 1.3
    indicator.calculate()
    assert indicator.result.label == "green"
    assert verify(indicator.result.description)


@pytest.mark.asyncio
@asyncpg_recorder.use_cassette
@oqapi_vcr.use_cassette
async def test_create_figure(
    topic_land_cover,
    feature_germany_heidelberg,
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_germany_heidelberg,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert verify_plotly(indicator.result.figure)
