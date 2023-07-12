import os
import unittest

import toml

from ohsome_quality_analyst import __version__ as oqt_version


class TestVersion(unittest.TestCase):
    def test_version(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "pyproject.toml"
        )
        with open(infile, "r") as fo:
            project_file = toml.load(fo)
            pyproject_version = project_file["tool"]["poetry"]["version"]
        self.assertEqual(pyproject_version, oqt_version)


if __name__ == "__main__":
    unittest.main()
