import pytest

from ohsome_quality_analyst.utils.exceptions import (
    GeoJsonError,
    GeoJsonGeometryTypeError,
    GeoJsonObjectTypeError,
    IndicatorTopicError,
    ValidationError,
)
from ohsome_quality_analyst.utils.validators import (
    validate_geojson,
    validate_indicator_topic_combination,
)


def test_validate_geojson_feature_collection_single(
    feature_collection_germany_heidelberg,
):
    # Single feature
    validate_geojson(feature_collection_germany_heidelberg)


def test_validate_geojson_feature_collection(
    feature_collection_germany_heidelberg_bahnstadt_bergheim,
):
    # Multiple features
    validate_geojson(feature_collection_germany_heidelberg_bahnstadt_bergheim)


def test_validate_geojson_invalid_geometry(feature_collection_invalid):
    # Invalid Polygon geometry
    with pytest.raises((GeoJsonError, ValidationError)):
        validate_geojson(feature_collection_invalid)


# TODO
@pytest.mark.skip(reason="Support for Feature will be discontinued.")
def test_validate_geojson_unsupported_object_type_feature(feature_germany_heidelberg):
    # Only GeoJson Feature Collection are supported not Feature
    with pytest.raises((GeoJsonObjectTypeError, ValidationError)):
        validate_geojson(feature_germany_heidelberg)


def test_validate_geojson_unsupported_object_type(geojson_unsupported_object_type):
    # Only GeoJson Feature Collection are supported not Geometry
    with pytest.raises((GeoJsonObjectTypeError, ValidationError)):
        validate_geojson(geojson_unsupported_object_type)


def test_validate_geojson_unsupported_geometry_type(
    feature_collection_unsupported_geometry_type,
):
    # Only a collection of features with geometry type Polygon and MultiPolygon are
    # supported.
    with pytest.raises((GeoJsonGeometryTypeError, ValidationError)):
        validate_geojson(feature_collection_unsupported_geometry_type)


def test_validate_indicator_topic_combination():
    validate_indicator_topic_combination("minimal", "minimal")


def test_validate_indicator_topic_combination_invalid():
    with pytest.raises((IndicatorTopicError, ValidationError)):
        validate_indicator_topic_combination("minimal", "building_count")
