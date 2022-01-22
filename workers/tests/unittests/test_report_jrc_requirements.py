import unittest
from unittest.mock import Mock

from ohsome_quality_analyst.reports.jrc_requirements.report import JrcRequirements

from .utils import get_geojson_fixture


class TestReportJrcRequirements(unittest.TestCase):
    # TODO: Test case for indicator.result undefined
    def test_combine_indicators_mean(self):

        geometry = get_geojson_fixture("heidelberg-altstadt-geometry.geojson")
        report = JrcRequirements(geometry)
        report.set_indicator_layer()

        # Mock indicator objects with a fixed result value
        for _ in report.indicator_layer:
            indicator = Mock()
            indicator.result = Mock()
            indicator.result.value = 0.5
            report.indicators.append(indicator)

        report.combine_indicators()

        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.description)
        # Should be the mean of all indicator result values
        self.assertEqual(report.result.value, 0.5)


if __name__ == "__main__":
    unittest.main()
