import asyncio
import unittest

from ohsome_quality_analyst.oqt import create_indicator
from ohsome_quality_analyst.reports.jrc_requirements.report import JrcRequirements


class TestReportJrcRequirements(unittest.TestCase):
    def setUp(self):
        # Test region in Heidelberg
        self.dataset_name = "test_regions"
        self.feature_id = 14

    def test(self):
        report = JrcRequirements(dataset=self.dataset_name, feature_id=self.feature_id)
        report.set_indicator_layer()
        for indicator_name, layer_name in report.indicator_layer:
            indicator = asyncio.run(
                create_indicator(
                    indicator_name,
                    layer_name,
                    report.bpolys,
                    report.dataset,
                    report.feature_id,
                )
            )
            report.indicators.append(indicator)
        report.combine_indicators()
        self.assertIsNotNone(report.result.label)
        self.assertIsNotNone(report.result.value)
        self.assertIsNotNone(report.result.description)


if __name__ == "__main__":
    unittest.main()
