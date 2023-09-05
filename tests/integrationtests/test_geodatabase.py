import asyncio
import unittest

import pytest
from geojson_pydantic import Polygon

import ohsome_quality_api.geodatabase.client as db_client
from ohsome_quality_api.api.request_models import FeatureWithOptionalProperties

pytestmark = pytest.mark.skip("dependency on database setup.")


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
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
):
    result = asyncio.run(
        db_client.get_shdi(feature_collection_heidelberg_bahnstadt_bergheim_weststadt)
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
    geom = Polygon(
        type="Polygon",
        coordinates=[
            [
                [13.610687255859375, 48.671919512374565],
                [14.0350341796875, 48.671919512374565],
                [14.0350341796875, 48.865618158309374],
                [13.610687255859375, 48.865618158309374],
                [13.610687255859375, 48.671919512374565],
            ]
        ],
    )
    result = asyncio.run(
        db_client.get_shdi(FeatureWithOptionalProperties(geometry=geom))
    )
    assert isinstance(result[0]["shdi"], float)
    assert result[0]["shdi"] <= 1.0


if __name__ == "__main__":
    unittest.main()
