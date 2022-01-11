import os
import unittest

import geojson

import ohsome_quality_analyst.raster.client as raster_client
from ohsome_quality_analyst.utils.definitions import get_raster_dataset


class TestRaster(unittest.TestCase):
    def setUp(self):
        self.raster = get_raster_dataset("GHS_BUILT_R2018A")

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures/heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            self.feature = geojson.load(f)

    def test_get_raster_path(self, *args):
        """Test if no error gets raises."""
        path = raster_client.get_raster_path(self.raster)
        self.assertIsInstance(path, str)

    def test_get_zonal_stats(self, *args):
        expected = {
            "count": 2,
            "max": 73.3844985961914,
            "mean": 70.12319946289062,
            "min": 66.86190032958984,
        }
        result = raster_client.get_zonal_stats(
            self.feature,
            self.raster,
        )
        self.assertEqual(expected, result[0])
