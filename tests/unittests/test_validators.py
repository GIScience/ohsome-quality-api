from unittest import mock

import pytest

from ohsome_quality_api.utils.exceptions import (
    IndicatorTopicCombinationError,
    InvalidCRSError,
    SizeRestrictionError,
)
from ohsome_quality_api.utils.validators import (
    validate_area,
    validate_indicator_topic_combination,
)
from tests.unittests.utils import get_geojson_fixture


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


def test_wrong_crs():
    with pytest.raises(InvalidCRSError) as exc_info:
        get_geojson_fixture("heidelberg-altstadt-epsg32632.geojson")

    expected_message = "Invalid CRS. GeoJSON must be in WGS84 (EPSG:4326)."
    assert str(exc_info.value.message) == expected_message
