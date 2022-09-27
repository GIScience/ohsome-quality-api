from unittest.mock import Mock

import pytest

from ohsome_quality_analyst.indicators.minimal.indicator import (
    Minimal as MinimalIndicator,
)
from ohsome_quality_analyst.reports.minimal.report import Minimal as MinimalReport

from .utils import get_geojson_fixture, get_layer_fixture


class TestBaseReport:
    @pytest.fixture
    def feature(self):
        return get_geojson_fixture("heidelberg-altstadt-feature.geojson")

    @pytest.fixture
    def layer(self):
        return get_layer_fixture("minimal")

    def test_as_feature(self, feature, layer):
        indicator = MinimalIndicator(feature=feature, layer=layer)
        report = MinimalReport(feature=feature, indicator_layer=indicator)
        report.set_indicator_layer()
        for _ in report.indicator_layer:
            report.indicators.append(indicator)

        feature = report.as_feature(flatten=True, include_data=True)
        assert feature.is_valid
        assert "indicators.0.data.count" in feature["properties"].keys()

    def test_attribution_class_property(self):
        assert isinstance(MinimalReport.attribution(), str)

    def test_blocking_red(self, feature, layer):
        report = MinimalReport(feature, blocking_red=True)
        report.set_indicator_layer()

        # Mock indicator objects with a fixed result value
        for i, _ in enumerate(report.indicator_layer):
            if i == 0:
                indicator = Mock()
                indicator.result = Mock()
                indicator.result.class_ = 1
                indicator.result.html = "foo"
                report.indicators.append(indicator)
            else:
                indicator = Mock()
                indicator.result = Mock()
                indicator.result.class_ = 5
                indicator.result.html = "foo"
                report.indicators.append(indicator)

        report.combine_indicators()
        assert report.result.class_ == 1 and report.result.label == "red"

    def test_blocking_undefined(self, feature, layer):
        report = MinimalReport(feature, blocking_undefined=True)
        report.set_indicator_layer()

        # Mock indicator objects with a fixed result value
        for i, _ in enumerate(report.indicator_layer):
            if i == 0:
                indicator = Mock()
                indicator.result = Mock()
                indicator.result.class_ = None
                indicator.result.html = "foo"
                report.indicators.append(indicator)
            else:
                indicator = Mock()
                indicator.result = Mock()
                indicator.result.class_ = 5
                indicator.result.html = "foo"
                report.indicators.append(indicator)

        report.combine_indicators()
        assert report.result.class_ is None and report.result.label == "undefined"

    def test_no_blocking(self, feature, layer):
        report = MinimalReport(feature)
        report.set_indicator_layer()

        # Mock indicator objects with a fixed result value
        for i, _ in enumerate(report.indicator_layer):
            if i == 0:
                indicator = Mock()
                indicator.result = Mock()
                indicator.result.class_ = None
                indicator.result.html = "foo"
                report.indicators.append(indicator)
            else:
                indicator = Mock()
                indicator.result = Mock()
                indicator.result.class_ = 5
                indicator.result.html = "foo"
                report.indicators.append(indicator)

        report.combine_indicators()
        assert report.result.label != "undefined" and report.result.label != "red"
