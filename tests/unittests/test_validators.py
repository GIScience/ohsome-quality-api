from unittest import mock

import pytest

from ohsome_quality_api.utils.exceptions import (
    AttributeTopicCombinationError,
    IndicatorTopicCombinationError,
    SizeRestrictionError,
)
from ohsome_quality_api.utils.validators import (
    validate_area,
    validate_attribute_topic_combination,
    validate_indicator_topic_combination,
)


def test_validate_attribute_topic_combination_with_valid_combination():
    validate_attribute_topic_combination("maxspeed", "roads")


def test_validate_attribute_topic_combination_with_invalid_topic():
    """As the method under test requires individually valid arguments
    the arguments given lead to a KeyError."""
    with pytest.raises(KeyError):
        validate_attribute_topic_combination("maxspeed", "xxxxx")


def test_validate_attribute_topic_combination_with_invalid_combination():
    with pytest.raises(AttributeTopicCombinationError):
        validate_attribute_topic_combination("maxspeed", "building-count")


def test_validate_indicator_topic_combination():
    validate_indicator_topic_combination("minimal", "minimal")


def test_validate_indicator_topic_combination_invalid():
    with pytest.raises(IndicatorTopicCombinationError):
        validate_indicator_topic_combination("minimal", "building-count")


@mock.patch.dict(
    "os.environ",
    {"OQAPI_GEOM_SIZE_LIMIT": "1000"},
    clear=True,
)
def test_validate_area(feature_germany_heidelberg):
    # expect not exceptions
    validate_area(feature_germany_heidelberg)


@mock.patch.dict(
    "os.environ",
    {"OQAPI_GEOM_SIZE_LIMIT": "1"},
    clear=True,
)
def test_validate_area_exception(feature_germany_heidelberg):
    with pytest.raises(SizeRestrictionError):
        validate_area(feature_germany_heidelberg)
