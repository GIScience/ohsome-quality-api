from geojson import Feature, FeatureCollection, GeoJSON, MultiPolygon, Polygon

from ohsome_quality_analyst.definitions import get_valid_indicators
from ohsome_quality_analyst.utils.exceptions import (
    GeoJSONError,
    GeoJSONGeometryTypeError,
    GeoJSONObjectTypeError,
    IndicatorTopicCombinationError,
)


def validate_indicator_topic_combination(indicator: str, topic: str):
    if indicator not in get_valid_indicators(topic):
        raise IndicatorTopicCombinationError(indicator, topic)


def validate_geojson(bpolys: GeoJSON):
    """Validate GeoJSON object."""
    if not bpolys.is_valid:
        raise GeoJSONError(errors=bpolys.errors())
    elif isinstance(bpolys, FeatureCollection):
        for feature in bpolys["features"]:
            validate_geojson(feature)
    elif isinstance(bpolys, Feature):
        if not isinstance(bpolys.geometry, Polygon | MultiPolygon):
            raise GeoJSONGeometryTypeError()
    else:
        raise GeoJSONObjectTypeError()
