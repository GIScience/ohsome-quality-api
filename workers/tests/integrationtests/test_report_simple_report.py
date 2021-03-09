import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.oqt import create_indicator
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport


class TestReportSimpleReport(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.report = SimpleReport(bpolys=bpolys)

    def test(self):
        self.report.set_indicator_layer()
        for indicator_name, layer_name in self.report.indicator_layer:
            indicator = asyncio.run(
                create_indicator(
                    indicator_name,
                    layer_name,
                    self.report.bpolys,
                    self.report.dataset,
                    self.report.feature_id,
                )
            )
            self.report.indicators.append(indicator)
        self.report.combine_indicators()
        self.assertIsNotNone(self.report.result.label)
        self.assertIsNotNone(self.report.result.value)
        self.assertIsNotNone(self.report.result.description)


if __name__ == "__main__":
    unittest.main()
