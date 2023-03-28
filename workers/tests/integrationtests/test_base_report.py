from unittest.mock import Mock

import pytest

from ohsome_quality_analyst.indicators.minimal.indicator import (
    Minimal as MinimalIndicator,
)
from ohsome_quality_analyst.reports.minimal.report import Minimal as MinimalReport

from .utils import get_geojson_fixture, get_topic_fixture


class TestBaseReport:
    @pytest.fixture
    def feature(self):
        return get_geojson_fixture("heidelberg-altstadt-feature.geojson")

    @pytest.fixture
    def topic(self):
        return get_topic_fixture("minimal")

    def test_as_feature(self, feature, topic):
        indicator = MinimalIndicator(feature=feature, topic=topic)
        report = MinimalReport(feature=feature)
        for _ in report.indicator_topic:
            report.indicators.append(indicator)

        feature = report.as_feature(flatten=True, include_data=True)
        assert feature.is_valid
        assert "indicators.0.data.count" in feature["properties"].keys()

    def test_attribution_class_property(self):
        assert isinstance(MinimalReport.attribution(), str)

    def test_blocking_red(self, feature, topic):
        report = MinimalReport(feature, blocking_red=True)

        # Mock indicator objects with a fixed result value
        for i, _ in enumerate(report.indicator_topic):
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

    def test_blocking_undefined(self, feature, topic):
        report = MinimalReport(feature, blocking_undefined=True)

        # Mock indicator objects with a fixed result value
        for i, _ in enumerate(report.indicator_topic):
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

    def test_no_blocking(self, feature, topic):
        report = MinimalReport(feature)

        # Mock indicator objects with a fixed result value
        for i, _ in enumerate(report.indicator_topic):
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

    def test_all_indicators_undefined(self, feature, topic):
        report = MinimalReport(feature, blocking_red=True)

        # Mock indicator objects with a fixed result value
        for _ in enumerate(report.indicator_topic):
            indicator = Mock()
            indicator.result = Mock()
            indicator.result.class_ = None
            indicator.result.html = "foo"
            report.indicators.append(indicator)

        report.combine_indicators()
        assert report.result.label == "undefined" and report.result.class_ is None
