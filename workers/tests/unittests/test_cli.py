"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import os
import unittest

from click.testing import CliRunner

from ohsome_quality_analyst.cli import cli


class TestCliUnit(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )

    def test_cli(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_list_indicators(self):
        result = self.runner.invoke(cli, ["list-indicators"])
        assert result.exit_code == 0

    def test_list_reports(self):
        result = self.runner.invoke(cli, ["list-reports"])
        assert result.exit_code == 0

    def test_list_layers(self):
        result = self.runner.invoke(cli, ["list-layers"])
        assert result.exit_code == 0

    def test_list_datasets(self):
        result = self.runner.invoke(cli, ["list-datasets"])
        assert result.exit_code == 0

    def test_create_indicator_help(self):
        result = self.runner.invoke(cli, ["create-indicator", "--help"])
        assert result.exit_code == 0

    def test_create_all_indicators(self):
        result = self.runner.invoke(
            cli,
            ["create-all-indicators"],
            input="N\n",
        )
        assert result.exit_code == 1


if __name__ == "__main__":
    unittest.main()
