from unittest import mock

import pytest

from ohsome_quality_api.utils.exceptions import (
    GeoJSONError,
    GeoJSONGeometryTypeError,
    GeoJSONObjectTypeError,
    InvalidCRSError,
    SizeRestrictionError,
)
from ohsome_quality_api.utils.validators import (
    validate_area,
    validate_geojson,
)
from tests.unittests.utils import get_geojson_fixture


def test_validate_geojson_feature_collection_single(
    feature_collection_germany_heidelberg,
):
    # Single feature
    validate_geojson(feature_collection_germany_heidelberg)


def test_validate_geojson_feature_collection(
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
):
    # Multiple features
    validate_geojson(feature_collection_heidelberg_bahnstadt_bergheim_weststadt)


def test_validate_geojson_invalid_geometry(feature_collection_invalid):
    # Invalid Polygon geometry
    with pytest.raises(GeoJSONError):
        validate_geojson(feature_collection_invalid)


def test_validate_geojson_unsupported_object_type_feature(feature_germany_heidelberg):
    # Only GeoJSON Feature Collection are supported not Feature
    with pytest.raises(GeoJSONObjectTypeError):
        validate_geojson(feature_germany_heidelberg)


def test_validate_geojson_unsupported_object_type(geojson_unsupported_object_type):
    # Only GeoJSON Feature Collection are supported not Geometry
    with pytest.raises(GeoJSONObjectTypeError):
        validate_geojson(geojson_unsupported_object_type)


def test_validate_geojson_unsupported_geometry_type(
    feature_collection_unsupported_geometry_type,
):
    # Only a collection of features with geometry type Polygon and MultiPolygon are
    # supported.
    with pytest.raises(GeoJSONGeometryTypeError):
        validate_geojson(feature_collection_unsupported_geometry_type)


@mock.patch.dict(
    "os.environ",
    {"OQAPI_GEOM_SIZE_LIMIT": "1000"},
    clear=True,
)
def test_validate_area(feature_germany_heidelberg):
    # expect not exceptions
    validate_area(feature_germany_heidelberg)


@mock.patch.dict(
    "os.environ",
    {"OQAPI_GEOM_SIZE_LIMIT": "1"},
    clear=True,
)
def test_validate_area_exception(feature_germany_heidelberg):
    with pytest.raises(SizeRestrictionError):
        validate_area(feature_germany_heidelberg)


def test_wrong_crs():
    feature = get_geojson_fixture("heidelberg-altstadt-epsg32632.geojson")
    with pytest.raises(InvalidCRSError) as exc_info:
        validate_geojson(feature)

    expected_message = (
        "Invalid CRS. The FeatureCollection must have the EPSG:4326 CRS or none."
    )
    assert str(exc_info.value.message) == expected_message


def test_custom_crs_short():
    def change_crs(geojson):
        geojson["crs"] = {"type": "name", "properties": {"name": "EPSG:4326"}}
        return geojson

    feature = get_geojson_fixture("heidelberg-altstadt-epsg32632.geojson")

    feature = change_crs(feature)

    validate_geojson(feature)


def test_custom_crs_long():
    def change_crs(geojson):
        geojson["crs"] = {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:EPSG::4326"},
        }
        return geojson

    feature = get_geojson_fixture("heidelberg-altstadt-epsg32632.geojson")

    feature = change_crs(feature)

    validate_geojson(feature)
