import unittest
from unittest.mock import Mock

from ohsome_quality_analyst.reports.multilevel_currentness.report import (
    MultilevelCurrentness,
)

from ..utils import load_geojson_fixture


class TestReportMultilevelCurrentness(unittest.TestCase):
    # TODO: Test case for indicator.result undefined
    def test_combine_indicators_mean(self):
        feature = load_geojson_fixture("feature-germany-heidelberg.geojson")
        report = MultilevelCurrentness(feature)

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
