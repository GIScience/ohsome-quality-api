import asyncio
import unittest
from unittest import mock

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport


class TestBaseReport(unittest.TestCase):
    def test_as_feature(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        indicator = GhsPopComparisonBuildings(feature=feature, layer=mock.Mock())
        report = SimpleReport(feature=feature)
        report.set_indicator_layer()
        for _ in report.indicator_layer:
            report.indicators.append(indicator)

        feature = report.as_feature()
        self.assertTrue(feature.is_valid)

        for i in (
            "indicators.0.data.pop_count",
            "indicators.0.data.area",
            "indicators.0.data.pop_count_per_sqkm",
            "indicators.0.data.feature_count",
            "indicators.0.data.feature_count_per_sqkm",
        ):
            self.assertIn(i, feature["properties"].keys())

    def test_attribution_class_property(self):
        self.assertIsNotNone(SimpleReport.attribution())
        self.assertIsInstance(SimpleReport.attribution(), str)
