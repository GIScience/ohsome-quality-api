"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import os
import tempfile
import unittest

import geojson
from click.testing import CliRunner

from ohsome_quality_analyst.cli.cli import cli

from .utils import oqt_vcr


class TestCliIntegration(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @oqt_vcr.use_cassette()
    def test_create_indicator_fcollection_outfile(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            outfile = os.path.join(
                tmpdirname,
                "result.geojson",
            )
            result = self.runner.invoke(
                cli,
                [
                    "create-indicator",
                    "-i",
                    "GhsPopComparisonBuildings",
                    "-l",
                    "building_count",
                    "--infile",
                    infile,
                    "--outfile",
                    outfile,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r") as testobject:
                testobject = geojson.load(testobject)
                self.assertTrue(testobject.is_valid)

    @oqt_vcr.use_cassette()
    def test_create_indicator_fcollection(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        result = self.runner.invoke(
            cli,
            [
                "create-indicator",
                "-i",
                "GhsPopComparisonBuildings",
                "-l",
                "building_count",
                "--infile",
                infile,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_indicator_feature_outfile(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            outfile = os.path.join(
                tmpdirname,
                "result.geojson",
            )
            result = self.runner.invoke(
                cli,
                [
                    "create-indicator",
                    "-i",
                    "GhsPopComparisonBuildings",
                    "-l",
                    "building_count",
                    "--infile",
                    infile,
                    "--outfile",
                    outfile,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r") as testobject:
                testobject = geojson.load(testobject)
                self.assertTrue(testobject.is_valid)

    @oqt_vcr.use_cassette()
    def test_create_indicator_feature(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        result = self.runner.invoke(
            cli,
            [
                "create-indicator",
                "-i",
                "GhsPopComparisonBuildings",
                "-l",
                "building_count",
                "--infile",
                infile,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_indicator_geometry_outfile(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            outfile = os.path.join(
                tmpdirname,
                "result.geojson",
            )
            result = self.runner.invoke(
                cli,
                [
                    "create-indicator",
                    "-i",
                    "GhsPopComparisonBuildings",
                    "-l",
                    "building_count",
                    "--infile",
                    infile,
                    "--outfile",
                    outfile,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r") as testobject:
                testobject = geojson.load(testobject)
                self.assertTrue(testobject.is_valid)

    @oqt_vcr.use_cassette()
    def test_create_indicator_geometry(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        result = self.runner.invoke(
            cli,
            [
                "create-indicator",
                "-i",
                "GhsPopComparisonBuildings",
                "-l",
                "building_count",
                "--infile",
                infile,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report_fcollection_outfile(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            outfile = os.path.join(
                tmpdirname,
                "result.geojson",
            )
            result = self.runner.invoke(
                cli,
                [
                    "create-report",
                    "-r",
                    "MinimalTestReport",
                    "--infile",
                    infile,
                    "--outfile",
                    outfile,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r") as testobject:
                testobject = geojson.load(testobject)
                self.assertTrue(testobject.is_valid)

    @oqt_vcr.use_cassette()
    def test_create_report_fcollection(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        result = self.runner.invoke(
            cli,
            [
                "create-report",
                "-r",
                "MinimalTestReport",
                "--infile",
                infile,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report_feature_outfile(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            outfile = os.path.join(
                tmpdirname,
                "result.geojson",
            )
            result = self.runner.invoke(
                cli,
                [
                    "create-report",
                    "-r",
                    "MinimalTestReport",
                    "--infile",
                    infile,
                    "--outfile",
                    outfile,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r") as testobject:
                testobject = geojson.load(testobject)
                self.assertTrue(testobject.is_valid)

    @oqt_vcr.use_cassette()
    def test_create_report_feature(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        result = self.runner.invoke(
            cli,
            [
                "create-report",
                "-r",
                "MinimalTestReport",
                "--infile",
                infile,
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @oqt_vcr.use_cassette()
    def test_create_report_geometry_outfile(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            outfile = os.path.join(
                tmpdirname,
                "result.geojson",
            )
            result = self.runner.invoke(
                cli,
                [
                    "create-report",
                    "-r",
                    "MinimalTestReport",
                    "--infile",
                    infile,
                    "--outfile",
                    outfile,
                ],
            )
            self.assertEqual(result.exit_code, 0)
            with open(outfile, "r") as testobject:
                testobject = geojson.load(testobject)
                self.assertTrue(testobject.is_valid)

    @oqt_vcr.use_cassette()
    def test_create_report_geometry(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        result = self.runner.invoke(
            cli,
            [
                "create-report",
                "-r",
                "MinimalTestReport",
                "--infile",
                infile,
            ],
        )
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
