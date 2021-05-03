"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import os
import unittest

import vcr
from click.testing import CliRunner

from ohsome_quality_analyst.cli import cli

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_BASENAME = os.path.splitext(os.path.basename(__file__))[0]


class TestCliIntegration(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
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

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def testCreateReport(self):
        result = self.runner.invoke(
            cli,
            ["create-report", "-r", "SimpleReport", "-d", "test_regions", "-f", "3"],
        )
        assert result.exit_code == 0


if __name__ == "__main__":
    unittest.main()
