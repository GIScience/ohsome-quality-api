import os
import unittest

import geojson

from ohsome_quality_tool.reports.remote_mapping_level_one.report import (
    RemoteMappingLevelOne,
)


class TestReportRemoteMappingLevelOne(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        self.report = RemoteMappingLevelOne(bpolys=bpolys)

    def test(self):
        self.report.create()
        self.assertIsNotNone(self.report.result.label)
        self.assertIsNotNone(self.report.result.value)
        self.assertIsNotNone(self.report.result.description)


if __name__ == "__main__":
    unittest.main()
