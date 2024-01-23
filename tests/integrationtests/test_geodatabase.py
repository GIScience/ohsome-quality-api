import asyncio
import unittest

import geojson
import pytest

import ohsome_quality_api.geodatabase.client as db_client
from ohsome_quality_api.indicators.building_comparison.indicator import (
    load_datasets_coverage_names,
    load_reference_datasets,
)

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


def test_get_building_area(feature_germany_berlin):
    result = asyncio.run(db_client.get_building_area(feature_germany_berlin))
    assert result[0]["area"] == 4842587.791645115


def test_get_reference_coverage():
    result = asyncio.run(
        db_client.get_reference_coverage(
            load_datasets_coverage_names(load_reference_datasets()), inverse=False
        )
    )
    for item in result:
        obj: geojson.MultiPolygon = geojson.loads(item)
        assert obj.is_valid
        assert isinstance(obj, geojson.MultiPolygon)


def test_get_eubucco_coverage_intersection_area_none(
    feature_collection_germany_heidelberg,
):
    bpoly = feature_collection_germany_heidelberg.features[0]
    result = asyncio.run(db_client.get_reference_coverage_intersection_area(bpoly))
    assert result == []


def test_get_eubucco_coverage_intersection_area(feature_germany_berlin):
    bpoly = feature_germany_berlin
    result = asyncio.run(db_client.get_reference_coverage_intersection_area(bpoly))
    assert pytest.approx(1.0, 0.1) == result[0]["area_ratio"]


def test_get_coverage_intersection(feature_germany_berlin):
    bpoly = feature_germany_berlin
    result = asyncio.run(db_client.get_reference_coverage_intersection(bpoly))
    assert result["geometry"].is_valid
    assert isinstance(result, geojson.feature.Feature)


if __name__ == "__main__":
    unittest.main()
