import unittest
from unittest.mock import Mock

from ohsome_quality_analyst.reports.sketchmap_fitness.report import SketchmapFitness

from .utils import get_geojson_fixture


class TestReportSketchmapFitness(unittest.TestCase):
    def test_combine_indicators_mean(self):
        geometry = get_geojson_fixture("heidelberg-altstadt-geometry.geojson")
        report = SketchmapFitness(geometry)
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
