import unittest
from unittest.mock import Mock

from ohsome_quality_analyst.reports.testing_report.report import TestingReport

from .utils import get_geojson_fixture


class TestReportTestingReport(unittest.TestCase):
    def test_combine_indicators_mean(self):
        geometry = get_geojson_fixture("heidelberg-altstadt-geometry.geojson")
        report = TestingReport(geometry)
        report.set_indicator_layer()

        # Mock indicator objects with a fixed result value
        for _ in report.indicator_layer:
            indicator = Mock()
            indicator.result = Mock()
            indicator.result.value = 0.5
            indicator.result.html = "foo"
            report.indicators.append(indicator)

        report.combine_indicators()
        report.create_html()

        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.description)
        self.assertIsNotNone(report.result.html)
        self.assertEqual(report.result.value, 0.5)


if __name__ == "__main__":
    unittest.main()
