"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import unittest

import geojson
from click.testing import CliRunner

from ohsome_quality_analyst.cli import cli

from .utils import oqt_vcr


class TestCliIntegration(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

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
                3,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_indicator_custom_fid_field_int(self):
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
                3,
                "--fid-field",
                "ogc_fid",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_indicator_custom_fid_field_str(self):
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
                "Heidelberg",  # equals ogc_fid 3
                "--fid-field",
                "name",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report(self):
        result = self.runner.invoke(
            cli,
            ["create-report", "-r", "SimpleReport", "-d", "regions", "-f", 3],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report_custom_fid_field_int(self):
        result = self.runner.invoke(
            cli,
            [
                "create-report",
                "-r",
                "SimpleReport",
                "-d",
                "regions",
                "-f",
                3,
                "--fid-field",
                "ogc_fid",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report_custom_fid_field_str(self):
        result = self.runner.invoke(
            cli,
            [
                "create-report",
                "-r",
                "SimpleReport",
                "-d",
                "regions",
                "-f",
                "Heidelberg",  # equals ogc_fid 3
                "--fid-field",
                "name",
            ],
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
