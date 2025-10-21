import os
import tomllib
import unittest

from ohsome_quality_api import __version__ as version


class TestVersion(unittest.TestCase):
    def test_version(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "pyproject.toml"
        )
        with open(infile, "rb") as fo:
            project_file = tomllib.load(fo)
            pyproject_version = project_file["project"]["version"]
        self.assertEqual(pyproject_version, version)


if __name__ == "__main__":
    unittest.main()
