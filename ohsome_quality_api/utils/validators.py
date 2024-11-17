from geojson import Feature, FeatureCollection, GeoJSON, MultiPolygon, Polygon
from pyproj import CRS

from ohsome_quality_api.attributes.definitions import (
    AttributeEnum,
    get_attributes,
)
from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.indicators.definitions import get_valid_indicators
from ohsome_quality_api.topics.models import BaseTopic
from ohsome_quality_api.utils.exceptions import (
    AttributeTopicCombinationError,
    GeoJSONError,
    GeoJSONGeometryTypeError,
    GeoJSONObjectTypeError,
    IndicatorTopicCombinationError,
    InvalidCRSError,
    SizeRestrictionError,
)
from ohsome_quality_api.utils.helper_geo import calculate_area


def validate_attribute_topic_combination(attribute: AttributeEnum, topic: BaseTopic):
    """As attributes are only meaningful for a certain topic,
    we need to check if the given combination is valid."""

    valid_attributes_for_topic = get_attributes()[topic.key]
    valid_attribute_names = [attribute for attribute in valid_attributes_for_topic]

    if attribute not in valid_attributes_for_topic:
        raise AttributeTopicCombinationError(
            attribute,
            topic.key,
            valid_attribute_names,
        )


def validate_indicator_topic_combination(indicator: str, topic: BaseTopic):
    if indicator not in get_valid_indicators(topic.key):
        raise IndicatorTopicCombinationError(indicator, topic)


def validate_geojson(bpolys: GeoJSON):
    """Validate GeoJSON object."""
    if not bpolys.is_valid:
        raise GeoJSONError(errors=bpolys.errors())
    elif isinstance(bpolys, FeatureCollection):
        for feature in bpolys["features"]:
            if not isinstance(feature.geometry, (Polygon, MultiPolygon)):
                raise GeoJSONGeometryTypeError()
    elif isinstance(bpolys, Feature):
        raise GeoJSONObjectTypeError()
    else:
        raise GeoJSONObjectTypeError()

    crs = bpolys.get("crs", None)
    if crs is not None:
        crs = CRS.from_string(crs.get("properties", {}).get("name", ""))
        crs_epsg = CRS.to_epsg(crs)
        if crs_epsg != 4326:
            raise InvalidCRSError()


def validate_area(feature: Feature):
    """Check area size of feature against size limit configuration value."""
    size_limit = float(get_config_value("geom_size_limit"))
    area = calculate_area(feature) / (1000 * 1000)  # sqkm
    if area > size_limit:
        raise SizeRestrictionError(size_limit, area)
