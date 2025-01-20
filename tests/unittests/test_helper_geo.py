from dataclasses import astuple

import pytest

from ohsome_quality_api.utils.helper_geo import calculate_area, get_bounding_box


def test_calculate_area(feature_germany_heidelberg):
    expected = 108852960.62891776  # derived from PostGIS ST_AREA
    result = calculate_area(feature_germany_heidelberg)
    assert result == pytest.approx(expected, abs=1e-3)


def test_get_bounding_box(feature_germany_heidelberg):
    result = get_bounding_box(feature_germany_heidelberg)
    expected = (8.5731788, 49.3520029, 8.7940496, 49.4596927)
    assert astuple(result) == pytest.approx(expected, abs=1e-6)
