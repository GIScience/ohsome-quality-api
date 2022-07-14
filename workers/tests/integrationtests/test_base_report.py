import asyncio
import unittest
from unittest import mock

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.minimal.indicator import (
    Minimal as MinimalIndicator,
)
from ohsome_quality_analyst.reports.minimal.report import Minimal as MinimalReport


class TestBaseReport(unittest.TestCase):
    def test_as_feature(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        indicator = MinimalIndicator(feature=feature, layer=mock.Mock())
        report = MinimalReport(feature=feature)
        report.set_indicator_layer()
        for _ in report.indicator_layer:
            report.indicators.append(indicator)

        feature = report.as_feature(flatten=True, include_data=True)
        assert feature.is_valid
        assert "indicators.0.data.count" in feature["properties"].keys()

    def test_attribution_class_property(self):
        assert MinimalReport.attribution() is not None
        assert isinstance(MinimalReport.attribution(), str)
