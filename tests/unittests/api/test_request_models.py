from contextvars import ContextVar

import pytest
from pydantic import ValidationError

from ohsome_quality_api.api.request_context import RequestContext
from ohsome_quality_api.api.request_models import (
    AttributeCompletenessFilterRequest,
    AttributeCompletenessKeyRequest,
    BaseBpolys,
    IndicatorRequest,
    LandCoverThematicAccuracyRequest,
)


@pytest.fixture
def mock_request_context_minimal(monkeypatch):
    """Mock request context for /indicators/minimal."""
    request_context: ContextVar[RequestContext] = ContextVar("request_context")
    request_context.set(RequestContext(path_parameters={"key": "minimal"}))
    monkeypatch.setattr(
        "ohsome_quality_api.api.request_models.request_context", request_context
    )


@pytest.fixture
def mock_request_context_land_cover_thematic_accuracy(monkeypatch):
    """Mock request context for /indicators/minimal."""
    request_context: ContextVar[RequestContext] = ContextVar("request_context")
    request_context.set(
        RequestContext(path_parameters={"key": "land-cover-thematic-accuracy"})
    )
    monkeypatch.setattr(
        "ohsome_quality_api.api.request_models.request_context", request_context
    )


@pytest.fixture
def mock_request_context_attribute_completeness(monkeypatch):
    """Mock request context for /indicators/attribute-completeness."""
    request_context: ContextVar[RequestContext] = ContextVar("request_context")
    request_context.set(
        RequestContext(path_parameters={"key": "attribute-completeness"})
    )
    monkeypatch.setattr(
        "ohsome_quality_api.api.request_models.request_context", request_context
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


@pytest.mark.usefixtures("mock_request_context_minimal")
def test_indicator_request_minimal(bpolys, topic_key_minimal):
    IndicatorRequest(bpolys=bpolys, topic=topic_key_minimal)


@pytest.mark.usefixtures("mock_request_context_minimal")
def test_indicator_request_invalid_indicator_topic_combination(
    bpolys, topic_key_building_count
):
    with pytest.raises(ValidationError):
        IndicatorRequest(bpolys=bpolys, topic=topic_key_building_count)


@pytest.mark.usefixtures("mock_request_context_minimal")
def test_indicator_request_include_figure(bpolys, topic_key_minimal):
    IndicatorRequest(bpolys=bpolys, topic=topic_key_minimal, include_figure=False)


def test_indicator_request_invalid_topic(bpolys):
    with pytest.raises(ValidationError):
        IndicatorRequest(bpolys=bpolys, topic="foo")


@pytest.mark.usefixtures("mock_request_context_attribute_completeness")
def test_attribute_completeness_missing_attribute(bpolys, topic_key_building_count):
    with pytest.raises(ValidationError):
        AttributeCompletenessKeyRequest(bpolys=bpolys, topic=topic_key_building_count)


@pytest.mark.usefixtures("mock_request_context_attribute_completeness")
def test_attribute_completeness_invalid_attribute(bpolys, topic_key_building_count):
    with pytest.raises(ValidationError):
        AttributeCompletenessKeyRequest(
            bpolys=bpolys,
            topic=topic_key_building_count,
            attributes="roads",
        )


@pytest.mark.usefixtures("mock_request_context_attribute_completeness")
def test_attribute_completeness_indicator_request_invalid_indicator_topic_combination(
    bpolys, topic_key_minimal, attribute_key_height
):
    with pytest.raises(ValidationError):
        AttributeCompletenessKeyRequest(
            bpolys=bpolys,
            topic=topic_key_minimal,
            attributes=attribute_key_height,
        )


@pytest.mark.usefixtures("mock_request_context_attribute_completeness")
def test_attribute_completeness(bpolys, topic_key_building_count):
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


@pytest.mark.usefixtures("mock_request_context_attribute_completeness")
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


@pytest.mark.usefixtures("mock_request_context_attribute_completeness")
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


def test_land_cover_thematic_accuracy_request(
    bpolys, mock_request_context_land_cover_thematic_accuracy
):
    # corine class parameter is optional (default all corine classes)
    LandCoverThematicAccuracyRequest(bpolys=bpolys, topic="land-cover")


def test_land_cover_thematic_accuracy_request_invalid_topic(
    bpolys, mock_request_context_land_cover_thematic_accuracy
):
    with pytest.raises(ValidationError):
        LandCoverThematicAccuracyRequest(bpolys=bpolys, topic="building-count")


def test_land_cover_thematic_accuracy_request_corine_class(
    bpolys, mock_request_context_land_cover_thematic_accuracy
):
    # Corine class 23 represents Pastures
    LandCoverThematicAccuracyRequest(
        bpolys=bpolys, topic="land-cover", corine_land_cover_class="23"
    )
    with pytest.raises(Exception):
        # Corine class 1 is invalid
        LandCoverThematicAccuracyRequest(
            bpolys=bpolys, topic="land-cover", corine_land_cover_class="1"
        )
