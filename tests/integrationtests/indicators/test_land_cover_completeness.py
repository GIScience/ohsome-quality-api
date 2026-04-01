import pytest
from pytest_approval.main import verify, verify_plotly

from ohsome_quality_api.indicators.land_cover_completeness.indicator import (
    LandCoverCompleteness,
)
from tests.integrationtests.utils import oqapi_vcr


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_preprocess(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    assert verify(str(indicator.osm_area_ratio))
    assert verify(indicator.result.timestamp_osm.isoformat())


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_calculate(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.result.label == "green"
    assert verify(str(indicator.osm_area_ratio))
    assert verify(str(indicator.result.value))
    assert verify(str(indicator.result.class_))
    assert verify(indicator.result.description)


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_calculate_above_100(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    indicator.osm_area_ratio = 1300000
    indicator.calculate()
    assert indicator.result.label == "green"
    assert verify(indicator.result.description)


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_figure(topic_land_cover, feature_land_cover):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert verify_plotly(indicator.result.figure)
