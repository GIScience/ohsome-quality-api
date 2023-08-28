import pytest

from ohsome_quality_api.utils.helper_geo import calculate_area


def test_calculate_area(feature_germany_heidelberg):
    expected = 108852960.62891776  # derived from PostGIS ST_AREA
    result = calculate_area(feature_germany_heidelberg)
    assert result == pytest.approx(expected, abs=1e-3)
