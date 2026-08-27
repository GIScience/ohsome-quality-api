import asyncpg_recorder
import pytest
from pytest_approval.main import verify, verify_plotly

from ohsome_quality_api.indicators.land_cover_completeness.indicator import (
    LandCoverCompleteness,
)
from tests.integrationtests.utils import oqapi_vcr


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
    assert indicator.area_feature == pytest.approx(108, abs=1)
    assert indicator.area_osm == pytest.approx(104, abs=1)
    assert indicator.result.timestamp_osm.strftime("%Y-%m-%d")


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
    indicator.area_osm = 130
    indicator.area_feature = 100
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
