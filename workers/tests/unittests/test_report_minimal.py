import unittest
from unittest.mock import Mock

from ohsome_quality_analyst.reports.minimal.report import Minimal

from .utils import get_geojson_fixture


class TestReportMinimal(unittest.TestCase):
    def test_combine_indicators_mean(self):
        geometry = get_geojson_fixture("heidelberg-altstadt-geometry.geojson")
        report = Minimal(geometry)

        # Mock indicator objects with a fixed result value
        for _ in report.indicator_topic:
            indicator = Mock()
            indicator.result = Mock()
            indicator.result.html = "foo"
            indicator.result.class_ = 1
            report.indicators.append(indicator)

        report.combine_indicators()
        report.create_html()

        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.description)
        self.assertIsNotNone(report.result.html)
        self.assertEqual(report.result.class_, 1)


if __name__ == "__main__":
    unittest.main()
