from geojson import Feature, FeatureCollection, GeoJSON, MultiPolygon, Polygon

from ohsome_quality_analyst.config import get_config_value
from ohsome_quality_analyst.indicators.definitions import get_valid_indicators
from ohsome_quality_analyst.utils.exceptions import (
    GeoJSONError,
    GeoJSONGeometryTypeError,
    GeoJSONObjectTypeError,
    IndicatorTopicCombinationError,
    SizeRestrictionError,
)
from ohsome_quality_analyst.utils.helper_geo import calculate_area


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


def validate_area(feature: Feature):
    """Check area size of feature against size limit configuration value."""
    size_limit = float(get_config_value("geom_size_limit"))
    area = calculate_area(feature) / (1000 * 1000)  # sqkm
    if area > size_limit:
        raise SizeRestrictionError(size_limit, area)
