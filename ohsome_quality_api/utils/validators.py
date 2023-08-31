from geojson_pydantic import Feature

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.indicators.definitions import get_valid_indicators
from ohsome_quality_api.utils.exceptions import (
    IndicatorTopicCombinationError,
    SizeRestrictionError,
)
from ohsome_quality_api.utils.helper_geo import calculate_area


def validate_indicator_topic_combination(indicator: str, topic: str):
    if indicator not in get_valid_indicators(topic):
        raise IndicatorTopicCombinationError(indicator, topic)


def validate_area(feature: Feature):
    """Check area size of feature against size limit configuration value."""
    size_limit = float(get_config_value("geom_size_limit"))
    area = calculate_area(feature) / (1000 * 1000)  # sqkm
    if area > size_limit:
        raise SizeRestrictionError(size_limit, area)
