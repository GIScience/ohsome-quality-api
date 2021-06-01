import asyncio
import os
import unittest

from ohsome_quality_analyst.api import load_bpolys


class TestApiUnit(unittest.TestCase):
    def test_validate_bpolys_size(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "europe.geojson",
        )
        with open(infile, "r") as f:
            bpolys = f.read()

        with self.assertRaises(ValueError):
            asyncio.run(load_bpolys(bpolys))
