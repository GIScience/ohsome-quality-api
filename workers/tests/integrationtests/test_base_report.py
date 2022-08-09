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
