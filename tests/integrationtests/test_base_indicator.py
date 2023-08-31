import plotly.graph_objects as pgo
import pytest

from ohsome_quality_api.indicators.minimal.indicator import Minimal
from ohsome_quality_api.indicators.models import Result

from .utils import get_geojson_fixture, get_topic_fixture


class TestBaseIndicator:
    @pytest.fixture
    def feature(self):
        return get_geojson_fixture("heidelberg-altstadt-feature.geojson")

    @pytest.fixture
    def topic(self):
        return get_topic_fixture("minimal")

    def test_as_dict(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        d = indicator.as_dict()
        assert set(("result", "metadata", "topic")) <= set(d.keys())  # subset
        assert "data" not in d.keys()

    def test_as_feature(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        feature = indicator.as_feature()
        assert feature.geometry == feature.geometry
        for key in ["result", "metadata", "topic"]:
            assert feature.properties[key] is not None
        assert feature.properties.get("data", None) is None

    def test_data_property(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        assert indicator.data is not None

    def test_attribution_class_property(self):
        assert isinstance(Minimal.attribution(), str)

    def test_figure(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
        # comment out for manual test
        # pio.show(indicator.result.figure)


class TestBaseResult:
    def test_label(self):
        result = Result(description="")
        assert result.label == "undefined"
        result.class_ = 4
        assert result.label == "green"
