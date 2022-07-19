"""
Testing Click Applications:
https://click.palletsprojects.com/en/7.x/testing/?highlight=testing
"""

import os
import unittest
from unittest import mock

from click.testing import CliRunner

from ohsome_quality_analyst.cli.cli import cli


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

    @mock.patch("ohsome_quality_analyst.oqt.create_indicator")
    def test_create_all_indicators_invlid_opts(self, mo):
        result = self.runner.invoke(
            cli,
            ["create-all-indicators"],
        )
        assert result.exit_code == 2

    @mock.patch("ohsome_quality_analyst.oqt.create_indicator", mock.AsyncMock())
    # Do not depend on database
    @mock.patch(
        "ohsome_quality_analyst.geodatabase.client.get_feature_ids", mock.AsyncMock()
    )
    def test_create_all_indicators_valid_opts(self):
        result = self.runner.invoke(
            cli,
            [
                "create-all-indicators",
                "-d",
                "regions",
            ],
            input="Y\n",
        )
        assert result.exit_code == 0
        result = self.runner.invoke(
            cli,
            [
                "create-all-indicators",
                "-d",
                "regions",
                "-l",
                "building-count",
            ],
            input="Y\n",
        )
        assert result.exit_code == 0
        result = self.runner.invoke(
            cli,
            [
                "create-all-indicators",
                "-d",
                "regions",
                "-i",
                "minimal",
            ],
            input="Y\n",
        )
        assert result.exit_code == 0
        result = self.runner.invoke(
            cli,
            [
                "create-all-indicators",
                "-d",
                "regions",
                "-i",
                "minimal",
                "-l",
                "minimal",
            ],
            input="Y\n",
        )
        assert result.exit_code == 0


if __name__ == "__main__":
    unittest.main()
