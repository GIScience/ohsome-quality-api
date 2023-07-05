import os
import unittest

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


if __name__ == "__main__":
    unittest.main()
