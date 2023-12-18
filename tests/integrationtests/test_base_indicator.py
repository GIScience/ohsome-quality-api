import asyncio

import plotly.graph_objects as pgo
import pytest
from geojson import Polygon

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

    def test_as_dict_include_data(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        d = indicator.as_dict(include_data=True)
        assert set(("result", "metadata", "topic", "data")) <= set(d.keys())  # subset
        assert "count" in d["data"]

    def test_as_feature(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        feature = indicator.as_feature()
        assert feature.is_valid
        assert feature.geometry == feature.geometry
        for prop in ("result", "metadata", "topic"):
            assert prop in feature["properties"]
        assert "data" not in feature["properties"]

    def test_as_feature_include_data(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        feature = indicator.as_feature(include_data=True)
        assert feature.is_valid
        for key in ("result", "metadata", "topic", "data"):
            assert key in feature["properties"]
        assert "count" in feature["properties"]["data"]

    def test_data_property(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        assert indicator.data is not None
        for key in ("result", "metadata", "topic", "feature"):
            assert key not in feature["properties"]

    def test_attribution_class_property(self):
        assert isinstance(Minimal.attribution(), str)

    def test_coverage(self):
        coverage = asyncio.run(Minimal.coverage(inverse=False))
        assert isinstance(coverage, Polygon)
        assert coverage.is_valid
        coverage_inversed = asyncio.run(Minimal.coverage(inverse=True))
        assert isinstance(coverage_inversed, Polygon)
        assert coverage_inversed.is_valid
        assert coverage != coverage_inversed

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
