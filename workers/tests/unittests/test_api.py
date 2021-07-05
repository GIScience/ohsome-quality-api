import asyncio
import os
import unittest

from geojson import Feature

from ohsome_quality_analyst.api import int_or_str_param_type, load_bpolys


class TestApiUnit(unittest.TestCase):
    def test_load_bpolys_invalid(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "ohsome-response-200-invalid.geojson",
        )
        with open(infile, "r") as f:
            bpolys = f.read()

        with self.assertRaises(ValueError):
            asyncio.run(load_bpolys(bpolys))

    def test_load_bpolys_size(self):
        # No error should be raised
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        with open(infile, "r") as file:
            bpolys = file.read()
        bpolys = asyncio.run(load_bpolys(bpolys))
        self.assertTrue(bpolys.is_valid)
        self.assertIsInstance(bpolys, Feature)

        # Error should be raised
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "europe.geojson",
        )
        with open(infile, "r") as f:
            bpolys = f.read()
        with self.assertRaises(ValueError):
            asyncio.run(load_bpolys(bpolys))

    def test_load_bpolys_featurecollection(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-featurecollection.geojson",
        )
        with open(infile, "r") as f:
            bpolys = f.read()
        with self.assertRaises(ValueError):
            asyncio.run(load_bpolys(bpolys))

    def test_load_bpolys_feature(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(infile, "r") as f:
            bpolys = f.read()
        bpolys = asyncio.run(load_bpolys(bpolys))
        self.assertTrue(bpolys.is_valid)
        self.assertIsInstance(bpolys, Feature)

    def test_load_bpolys_geometry(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-geometry.geojson",
        )
        with open(infile, "r") as f:
            bpolys = f.read()
        bpolys = asyncio.run(load_bpolys(bpolys))
        self.assertTrue(bpolys.is_valid)
        self.assertIsInstance(bpolys, Feature)

    def test_int_or_str_param_type(self):
        self.assertIsInstance(int_or_str_param_type("1"), int)
        self.assertIsInstance(int_or_str_param_type("a"), str)
