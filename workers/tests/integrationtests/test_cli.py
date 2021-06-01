"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import os
import unittest

import geojson
from click.testing import CliRunner

from ohsome_quality_analyst.cli import cli

from .utils import oqt_vcr


class TestCliIntegration(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator(self):
        result = self.runner.invoke(
            cli,
            [
                "create-indicator",
                "-i",
                "GhsPopComparisonBuildings",
                "-l",
                "building_count",
                "-d",
                "regions",
                "-f",
                "3",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report(self):
        result = self.runner.invoke(
            cli,
            ["create-report", "-r", "SimpleReport", "-d", "regions", "-f", "3"],
        )
        self.assertEqual(result.exit_code, 0)

    def test_get_available_regions(self):
        result = self.runner.invoke(
            cli,
            ["-q", "list-regions"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(geojson.loads(result.output).is_valid)


if __name__ == "__main__":
    unittest.main()
