import pytest

from ohsome_quality_api.ohsome_api import client
from tests.integrationtests.utils import oqapi_vcr

pytestmark = pytest.mark.asyncio


@oqapi_vcr.use_cassette
async def test_metadata():
    await client.metadata()


@pytest.mark.parametrize("measure", ["count", "length", "area"])
@oqapi_vcr.use_cassette()
async def test_features(feature, measure):
    result = await client.features(
        aoi=feature["geometry"],
        measure=measure,
        ohsome_filter="type:node and natural=tree",
        time_series={
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-04-17T00:00:00Z",
            "interval": "P1M",
        },
    )
    assert len(result["value"]) == 5


@pytest.mark.parametrize("measure", ["count", "length", "area"])
@oqapi_vcr.use_cassette()
async def test_currentness(feature, measure):
    result = await client.currentness(
        aoi=feature["geometry"],
        measure=measure,
        ohsome_filter="type:node and natural=tree",
        time_bins={
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-04-17T00:00:00Z",
            "binSize": "P1M",
        },
    )
    assert len(result["value"]) == 4


@oqapi_vcr.use_cassette()
async def test_activity_user(feature):
    result = await client.activity_users(
        aoi=feature["geometry"],
        ohsome_filter="type:node and natural=tree",
        time_bins={
            "start": "2026-01-01T00:00:00Z",
            "end": "2026-04-17T00:00:00Z",
            "binSize": "P1M",
        },
    )
    assert len(result["value"]) == 4
