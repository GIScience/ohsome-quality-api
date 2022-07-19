import asyncio
import os
from datetime import datetime

import pytest

from ohsome_quality_analyst.indicators.ghs_pop_comparison_roads.indicator import (
    GhsPopComparisonRoads,
)

from .utils import get_fixture_dir, get_geojson_fixture, get_layer_fixture, oqt_vcr


@pytest.fixture
def mock_env_oqt_data_dir(monkeypatch):
    directory = os.path.join(get_fixture_dir(), "rasters")
    monkeypatch.setenv("OQT_DATA_DIR", directory)


@oqt_vcr.use_cassette()
def test(mock_env_oqt_data_dir):
    feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
    layer = get_layer_fixture("major_roads_length")
    indicator = GhsPopComparisonRoads(feature=feature, layer=layer)

    asyncio.run(indicator.preprocess())
    assert indicator.pop_count is not None
    assert indicator.area is not None
    assert indicator.feature_length is not None
    assert indicator.attribution() is not None
    assert isinstance(indicator.result.timestamp_osm, datetime)
    assert isinstance(indicator.result.timestamp_oqt, datetime)

    indicator.calculate()
    assert indicator.result.label is not None
    assert indicator.result.value is not None
    assert indicator.result.description is not None
    assert indicator.pop_count_per_sqkm is not None

    indicator.create_figure()
    assert indicator.result.svg is not None
