import pytest

from ohsome_quality_analyst.base.indicator import Result
from ohsome_quality_analyst.indicators.minimal.indicator import Minimal

from .utils import get_geojson_fixture, get_layer_fixture


@pytest.fixture
def feature():
    return get_geojson_fixture("heidelberg-altstadt-feature.geojson")


@pytest.fixture
def layer():
    return get_layer_fixture("minimal")


def test_as_feature(feature, layer):
    indicator = Minimal(feature=feature, layer=layer)
    feature = indicator.as_feature()
    assert feature.is_valid
    assert feature.geometry == feature.geometry
    for prop in ("result", "metadata", "layer"):
        assert prop in feature["properties"]
    assert "data" not in feature["properties"]


def test_as_feature_include_data(feature, layer):
    indicator = Minimal(feature=feature, layer=layer)
    feature = indicator.as_feature(include_data=True)
    assert feature.is_valid
    for key in ("result", "metadata", "layer", "data"):
        assert key in feature["properties"]
    assert "count" in feature["properties"]["data"]


def test_as_feature_flatten(feature, layer):
    indicator = Minimal(feature=feature, layer=layer)
    feature = indicator.as_feature(flatten=True)
    assert feature.is_valid
    for key in (
        "result.value",
        "metadata.name",
        "layer.name",
    ):
        assert key in feature["properties"]


def test_data_property(feature, layer):
    indicator = Minimal(feature=feature, layer=layer)
    assert indicator.data is not None
    for key in ("result", "metadata", "layer", "feature"):
        assert key not in feature["properties"]


def test_attribution_class_property():
    assert isinstance(Minimal.attribution(), str)


def test_base_result_label():
    result = Result("", "", "")
    assert result.label == "undefined"
    result.class_ = 4
    assert result.label == "green"
