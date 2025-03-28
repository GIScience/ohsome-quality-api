import pytest
from pydantic import ValidationError

from ohsome_quality_api.api.request_models import (
    AttributeCompletenessFilterRequest,
    AttributeCompletenessKeyRequest,
    BaseBpolys,
    IndicatorRequest,
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
    with pytest.raises(ValidationError):
        BaseBpolys(bpolys=feature_collection_invalid)


def test_bpolys_unsupported_object_type_feature(feature_germany_heidelberg):
    with pytest.raises(ValidationError):
        BaseBpolys(bpolys=feature_germany_heidelberg)


def test_bpolys_unsupported_object_type(geojson_unsupported_object_type):
    with pytest.raises(ValidationError):
        BaseBpolys(bpolys=geojson_unsupported_object_type)


def test_bpolys_unsupported_geometry_type(feature_collection_unsupported_geometry_type):
    with pytest.raises(ValidationError):
        BaseBpolys(bpolys=feature_collection_unsupported_geometry_type)


def test_indicator_request_minimal(bpolys, topic_key_minimal):
    IndicatorRequest(bpolys=bpolys, topic=topic_key_minimal)


def test_indicator_request_include_figure(bpolys, topic_key_minimal):
    IndicatorRequest(bpolys=bpolys, topic=topic_key_minimal, include_figure=False)


def test_indicator_request_invalid_topic(bpolys):
    with pytest.raises(ValueError):
        IndicatorRequest(bpolys=bpolys, topic="foo")


def test_attribute_completeness_missing_attribute(bpolys, topic_key_building_count):
    with pytest.raises(ValueError):
        AttributeCompletenessKeyRequest(bpolys=bpolys, topic=topic_key_building_count)


def test_attribute_completeness_invalid_attribute(bpolys, topic_key_building_count):
    with pytest.raises(ValueError):
        AttributeCompletenessKeyRequest(
            bpolys=bpolys, topic=topic_key_building_count, attributes="foo"
        )


def test_attribute_completeness_single_attribute(
    bpolys,
    topic_key_building_count,
    attribute_key_height,
):
    AttributeCompletenessKeyRequest(
        bpolys=bpolys,
        topic=topic_key_building_count,
        attributes=attribute_key_height,
    )


def test_attribute_completeness_multiple_attributes(
    bpolys,
    topic_key_building_count,
    attribute_key_multiple,
):
    AttributeCompletenessKeyRequest(
        bpolys=bpolys,
        topic=topic_key_building_count,
        attributes=attribute_key_multiple,
    )


def test_attribute_completeness_attribute_filter(
    bpolys,
    topic_key_building_count,
    attribute_filter,
    attribute_title,
):
    AttributeCompletenessFilterRequest(
        bpolys=bpolys,
        topic=topic_key_building_count,
        attribute_filter=attribute_filter,
        attribute_title=attribute_title,
    )
