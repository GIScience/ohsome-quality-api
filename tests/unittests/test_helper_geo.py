import pytest

from ohsome_quality_api.utils.helper_geo import calculate_area


def test_calculate_area(feature_germany_heidelberg):
    # derived from PostGIS "SELECT ST_Area( ST_GeomFromGeoJSON(JSON_HERE)::geography)"
    expected = 108852943.11450204
    result = calculate_area(feature_germany_heidelberg)
    assert result == pytest.approx(expected, abs=0.03)


def test_calculate_area_multipolygon(feature_multipolygon_germany_heidelberg):
    # derived from PostGIS SELECT ST_Area( ST_GeomFromGeoJSON(JSON_HERE)::geography)
    expected = 1795635.9057149887
    result = calculate_area(feature_multipolygon_germany_heidelberg)
    assert result == pytest.approx(expected, abs=0.03)
