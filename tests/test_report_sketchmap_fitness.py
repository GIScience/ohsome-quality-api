import os
import unittest

import geojson

from ohsome_quality_tool.reports.sketchmap_fitness.report import SketchmapFitness


class TestReportSketchmapFitness(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.report = SketchmapFitness(bpolys=bpolys)

    def test(self):
        self.report.create_indicators()
        self.report.combine_indicators()
        self.assertIsNotNone(self.report.result.label)
        self.assertIsNotNone(self.report.result.value)
        self.assertIsNotNone(self.report.result.description)


if __name__ == "__main__":
    unittest.main()
