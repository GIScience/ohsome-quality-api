import unittest
from unittest.mock import Mock

from ohsome_quality_analyst.reports.sketchmap_fitness.report import SketchmapFitness

from ..utils import load_geojson_fixture


class TestReportSketchmapFitness(unittest.TestCase):
    def test_combine_indicators_mean(self):
        feature = load_geojson_fixture("feature-germany-heidelberg.geojson")
        report = SketchmapFitness(feature)

        # Mock indicator objects with a fixed result value
        for _ in report.indicator_topic:
            indicator = Mock()
            indicator.result = Mock()
            indicator.result.class_ = 1
            report.indicators.append(indicator)

        report.combine_indicators()

        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.description)
        self.assertEqual(report.result.class_, 1)


if __name__ == "__main__":
    unittest.main()
