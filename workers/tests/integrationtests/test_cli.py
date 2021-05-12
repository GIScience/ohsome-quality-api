"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import os
import unittest

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
    def testCreateIndicator(self):
        result = self.runner.invoke(
            cli,
            [
                "create-indicator",
                "-i",
                "GhsPopComparisonBuildings",
                "-l",
                "building_count",
                "-d",
                "test_regions",
                "-f",
                "3",
            ],
        )
        assert result.exit_code == 0

    @oqt_vcr.use_cassette()
    def testCreateReport(self):
        result = self.runner.invoke(
            cli,
            ["create-report", "-r", "SimpleReport", "-d", "test_regions", "-f", "3"],
        )
        assert result.exit_code == 0


if __name__ == "__main__":
    unittest.main()
