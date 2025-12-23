import asyncio

import plotly.graph_objects as pgo
import pytest
from approvaltests import verify
from geojson import Feature

from ohsome_quality_api.indicators.minimal.indicator import Minimal
from ohsome_quality_api.indicators.models import (
    IndicatorTemplates,
    Result,
)
from tests.approvaltests_namers import PytestNamer

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
        assert "data" not in d

    def test_as_dict_include_data(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        d = indicator.as_dict(include_data=True)
        assert set(("result", "metadata", "topic", "data")) <= set(d.keys())  # subset
        assert "count" in d["data"]

    def test_as_feature(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        feature_indicator = indicator.as_feature()
        assert feature_indicator.is_valid
        assert feature_indicator.geometry == feature.geometry
        for prop in ("result", "metadata", "topic"):
            assert prop in feature_indicator["properties"]
        assert "data" not in feature_indicator["properties"]

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
        for feature in coverage:
            assert isinstance(feature, Feature)
            assert feature.is_valid
            assert feature["geometry"] is not None
        coverage_default = asyncio.run(Minimal.coverage())
        for feature in coverage_default:
            assert isinstance(feature, Feature)
            assert feature.is_valid
            assert feature["geometry"] is not None
        assert coverage_default == coverage
        coverage_inversed = asyncio.run(Minimal.coverage(inverse=True))
        for feature in coverage_inversed:
            assert isinstance(feature, Feature)
            assert feature.is_valid
            assert feature["geometry"] is not None
        assert coverage != coverage_inversed
        assert coverage_default != coverage_inversed

    def test_figure(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
        # comment out for manual test
        # pio.show(indicator.result.figure)

    def test_get_template(self, feature, topic):
        indicator = Minimal(feature=feature, topic=topic)
        indicator.get_template()
        assert isinstance(indicator.templates, IndicatorTemplates)
        assert isinstance(indicator.result, Result)

    def test_get_template_translated(self, feature, topic, locale_de):
        indicator = Minimal(feature=feature, topic=topic)
        indicator.get_template()
        assert isinstance(indicator.templates, IndicatorTemplates)
        assert isinstance(indicator.result, Result)
        verify(indicator.templates.model_dump_json(indent=2), namer=PytestNamer())


class TestBaseResult:
    def test_label(self):
        result = Result(description="")
        assert result.label == "undefined"
        result.class_ = 4
        assert result.label == "green"
