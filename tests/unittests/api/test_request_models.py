import pytest
from pydantic import ValidationError

from ohsome_quality_analyst.api.request_models import BaseBpolys, IndicatorRequest
from ohsome_quality_analyst.utils.exceptions import (
    GeoJSONError,
    GeoJSONGeometryTypeError,
    GeoJSONObjectTypeError,
)


def test_bpolys_valid(
    feature_collection_germany_heidelberg,
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
):
    # Single Feature
    BaseBpolys(bpolys=feature_collection_germany_heidelberg)
    # Multiple Features
    BaseBpolys(bpolys=feature_collection_heidelberg_bahnstadt_bergheim_weststadt)


def test_bpolys_invalid(feature_collection_invalid):
    with pytest.raises((GeoJSONError, ValidationError)):
        BaseBpolys(bpolys=feature_collection_invalid)


def test_bpolys_unsupported_object_type_feature(feature_germany_heidelberg):
    with pytest.raises((GeoJSONObjectTypeError, ValidationError)):
        BaseBpolys(bpolys=feature_germany_heidelberg)


def test_bpolys_unsupported_object_type(geojson_unsupported_object_type):
    with pytest.raises((GeoJSONObjectTypeError, ValidationError)):
        BaseBpolys(bpolys=geojson_unsupported_object_type)


def test_bpolys_unsupported_geometry_type(feature_collection_unsupported_geometry_type):
    with pytest.raises((GeoJSONGeometryTypeError, ValidationError)):
        BaseBpolys(bpolys=feature_collection_unsupported_geometry_type)


def test_indicator_request(bpolys, topic_key_minimal):
    IndicatorRequest(bpolys=bpolys, topic=topic_key_minimal)


def test_indicator_request_invalid_topic(bpolys):
    with pytest.raises(ValueError):
        IndicatorRequest(bpolys=bpolys, topic="foo")
