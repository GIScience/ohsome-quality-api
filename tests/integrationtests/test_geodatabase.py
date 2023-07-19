import asyncio
import unittest

import geojson
import pytest

import ohsome_quality_analyst.geodatabase.client as db_client

# pytestmark = pytest.mark.skip("dependency on database setup.")


def test_get_connection():
    async def _test_get_connection():
        async with db_client.get_connection() as conn:
            return await conn.fetchrow("SELECT 1")

    result = asyncio.run(_test_get_connection())
    assert result[0] == 1


def test_get_shdi_single_intersection_feature(feature):
    """Input geometry intersects only with one SHDI region."""
    result = asyncio.run(db_client.get_shdi(feature))
    assert isinstance(result[0]["shdi"], float)
    assert result[0]["shdi"] <= 1.0
    assert len(result) == 1


def test_get_shdi_single_intersection_featurecollection(
    feature_collection_germany_heidelberg_bahnstadt_bergheim,
):
    result = asyncio.run(
        db_client.get_shdi(feature_collection_germany_heidelberg_bahnstadt_bergheim)
    )
    assert len(result) == 3
    assert isinstance(result[0]["shdi"], float)
    assert result[0]["shdi"] <= 1.0
    assert isinstance(result[1]["shdi"], float)
    assert result[1]["shdi"] <= 1.0
    assert isinstance(result[2]["shdi"], float)
    assert result[2]["shdi"] <= 1.0


def test_get_shdi_type_error(feature):
    with pytest.raises(TypeError):
        asyncio.run(db_client.get_shdi(feature.geometry))


def test_get_shdi_multiple_intersections():
    """Input geometry intersects with multiple SHDI-regions."""
    geom = geojson.Polygon(
        [
            [
                [13.610687255859375, 48.671919512374565],
                [14.0350341796875, 48.671919512374565],
                [14.0350341796875, 48.865618158309374],
                [13.610687255859375, 48.865618158309374],
                [13.610687255859375, 48.671919512374565],
            ]
        ],
    )
    result = asyncio.run(db_client.get_shdi(geojson.Feature(geometry=geom)))
    assert isinstance(result[0]["shdi"], float)
    assert result[0]["shdi"] <= 1.0


if __name__ == "__main__":
    unittest.main()
