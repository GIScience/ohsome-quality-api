import os
import unittest

from click.testing import CliRunner

from ohsome_quality_tool.cli import cli


class TestCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )

    def testCli(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def testListIndicators(self):
        result = self.runner.invoke(cli, ["list-indicators"])
        assert result.exit_code == 0

    def testListReports(self):
        result = self.runner.invoke(cli, ["list-reports"])
        assert result.exit_code == 0

    def testListLayers(self):
        result = self.runner.invoke(cli, ["list-layers"])
        assert result.exit_code == 0

    def testCreateIndicator(self):
        result = self.runner.invoke(
            cli,
            [
                "create-indicator",
                "--indicator-name",
                "GhsPopComparison",
                "--layer-name",
                "building_count",
                "--infile",
                self.infile,
            ],
        )
        assert result.exit_code == 0

    def testCreateReport(self):
        result = self.runner.invoke(
            cli,
            [
                "create-report",
                "--report-name",
                "SimpleReport",
                "--infile",
                self.infile,
            ],
        )
        assert result.exit_code == 0


if __name__ == "__main__":
    unittest.main()
