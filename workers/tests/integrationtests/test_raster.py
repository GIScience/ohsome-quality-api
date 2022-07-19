import os

import pytest

import ohsome_quality_analyst.raster.client as raster_client
from ohsome_quality_analyst.definitions import get_raster_dataset

from .utils import get_fixture_dir, get_geojson_fixture


@pytest.fixture
def mock_env_oqt_data_dir(monkeypatch):
    directory = os.path.join(get_fixture_dir(), "rasters")
    monkeypatch.setenv("OQT_DATA_DIR", directory)


def test_get_raster_path(mock_env_oqt_data_dir):
    raster = get_raster_dataset("GHS_BUILT_R2018A")
    path = raster_client.get_raster_path(raster)
    assert isinstance(path, str)


def test_get_zonal_stats(mock_env_oqt_data_dir):
    raster = get_raster_dataset("GHS_BUILT_R2018A")
    feature = get_geojson_fixture("algeria-touggourt-feature.geojson")

    expected = [
        {
            "min": 0.0,
            "max": 46.7505989074707,
            "mean": 1.6491034092047276,
            "count": 234,
        }
    ]
    result = raster_client.get_zonal_stats(
        feature,
        raster,
    )
    assert expected == result
