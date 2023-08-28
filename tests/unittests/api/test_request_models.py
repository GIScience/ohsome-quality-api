import pytest
from geojson_pydantic import FeatureCollection
from pydantic import ValidationError

from ohsome_quality_analyst.api.request_models import BaseBpolys, IndicatorRequest
from ohsome_quality_analyst.utils.exceptions import (
    GeoJSONError,
    GeoJSONObjectTypeError,
)


def test_bpolys_valid(
    feature_collection_germany_heidelberg,
    feature_collection_heidelberg_bahnstadt_bergheim_weststadt,
):
    # Single Feature
    BaseBpolys(bpolys=feature_collection_germany_heidelberg.model_dump())
    # Multiple Features
    BaseBpolys(
        bpolys=feature_collection_heidelberg_bahnstadt_bergheim_weststadt.model_dump()
    )


def test_bpolys_invalid(feature_collection_invalid):
    with pytest.raises((GeoJSONError, ValidationError)):
        FeatureCollection(**feature_collection_invalid)


def test_bpolys_unsupported_object_type_feature(feature_germany_heidelberg):
    with pytest.raises((GeoJSONObjectTypeError, ValidationError)):
        BaseBpolys(bpolys=feature_germany_heidelberg.model_dump())


# todo: should no longer be needed?
"""
def test_bpolys_unsupported_object_type(geojson_unsupported_object_type):
    with pytest.raises((GeoJSONObjectTypeError, ValidationError)):
        BaseBpolys(bpolys=geojson_unsupported_object_type)

"""
# todo: should no longer be needed?
"""
def test_bpolys_unsupported_geometry_type(feature_collection_unsupported_geometry_type):
    with pytest.raises((GeoJSONGeometryTypeError, ValidationError)):
        BaseBpolys(bpolys=feature_collection_unsupported_geometry_type)
"""


def test_indicator_request_minimal(
    feature_collection_germany_heidelberg, topic_key_minimal
):
    IndicatorRequest(
        bpolys=feature_collection_germany_heidelberg.model_dump(),
        topic=topic_key_minimal,
    )


def test_indicator_request_include_figure(
    feature_collection_germany_heidelberg, topic_key_minimal
):
    IndicatorRequest(
        bpolys=feature_collection_germany_heidelberg.model_dump(),
        topic=topic_key_minimal,
        include_figure=False,
    )


def test_indicator_request_include_data(
    feature_collection_germany_heidelberg, topic_key_minimal
):
    IndicatorRequest(
        bpolys=feature_collection_germany_heidelberg.model_dump(),
        topic=topic_key_minimal,
        include_data=True,
    )


def test_indicator_request_include_all(
    feature_collection_germany_heidelberg, topic_key_minimal
):
    IndicatorRequest(
        bpolys=feature_collection_germany_heidelberg.model_dump(),
        topic=topic_key_minimal,
        include_figure=False,
        include_data=True,
    )


def test_indicator_request_invalid_topic(feature_collection_germany_heidelberg):
    with pytest.raises(ValueError):
        IndicatorRequest(
            bpolys=feature_collection_germany_heidelberg.model_dump(), topic="foo"
        )
