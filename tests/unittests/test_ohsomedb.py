import asyncpg_recorder
import pytest
from geojson import Feature

from ohsome_quality_api import ohsomedb

pytestmark = pytest.mark.asyncio


@pytest.fixture
def filter_buildings() -> str:
    return "building=* and building!=no and geometry:polygon"


@pytest.fixture
def filter_highways() -> str:
    return "highway in (motorway, trunk, primary, secondary, tertiary, residential, service, living_street, trunk_link, motorway_link, primary_link, secondary_link, tertiary_link, unclassified) and geometry:line"  # noqa


@asyncpg_recorder.use_cassette
async def test_contributions_count(
    feature_germany_heidelberg: Feature,
    filter_buildings: str,
):
    results = await ohsomedb.contributions(
        aggregation="count",
        bpolys=feature_germany_heidelberg["geometry"],
        filter_=filter_buildings,
    )
    assert sum([r["contribution"] for r in results]) > 0


@asyncpg_recorder.use_cassette
async def test_contributions_area(
    feature_germany_heidelberg: Feature,
    filter_buildings: str,
):
    results = await ohsomedb.contributions(
        aggregation="area",
        bpolys=feature_germany_heidelberg["geometry"],
        filter_=filter_buildings,
    )
    assert sum([r["contribution"] for r in results]) > 0


@asyncpg_recorder.use_cassette
async def test_contributions_length(
    feature_germany_heidelberg: Feature,
    filter_highways: str,
):
    results = await ohsomedb.contributions(
        aggregation="length",
        bpolys=feature_germany_heidelberg["geometry"],
        filter_=filter_highways,
    )
    assert sum([r["contribution"] for r in results]) > 0


@asyncpg_recorder.use_cassette
async def test_users_count(
    feature_germany_heidelberg: Feature,
    filter_highways: str,
):
    results = await ohsomedb.users(
        bpolys=feature_germany_heidelberg["geometry"],
        filter_=filter_highways,
    )
    assert sum([r["user"] for r in results]) > 0


@asyncpg_recorder.use_cassette
async def test_elements_count(
    feature_germany_heidelberg: Feature,
    filter_buildings: str,
):
    results = await ohsomedb.elements(
        aggregation="count",
        bpolys=feature_germany_heidelberg["geometry"],
        filter_=filter_buildings,
    )
    raw = [r["element"] for r in results]
    assert sum(raw) > 0
