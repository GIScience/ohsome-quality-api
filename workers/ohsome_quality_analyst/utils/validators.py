from geojson import Feature, FeatureCollection, GeoJSON, MultiPolygon, Polygon

from ohsome_quality_analyst.definitions import get_valid_indicators
from ohsome_quality_analyst.utils.exceptions import (
    GeoJsonError,
    GeoJsonGeometryTypeError,
    GeoJsonObjectTypeError,
    IndicatorTopicError,
)


def validate_indicator_topic_combination(indicator: str, topic: str):
    if indicator not in get_valid_indicators(topic):
        raise IndicatorTopicError(indicator, topic)


def validate_geojson(bpolys: GeoJSON):
    """Validate GeoJSON object."""
    if not bpolys.is_valid:
        raise GeoJsonError(errors=bpolys.errors)
    elif isinstance(bpolys, FeatureCollection):
        for feature in bpolys["features"]:
            validate_geojson(feature)
    elif isinstance(bpolys, Feature):
        if not isinstance(bpolys.geometry, (Polygon, MultiPolygon)):
            raise GeoJsonGeometryTypeError()
    else:
        raise GeoJsonObjectTypeError()
