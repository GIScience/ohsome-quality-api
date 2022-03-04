import os
import unittest
from unittest import mock

import geojson

import ohsome_quality_analyst.raster.client as raster_client
from ohsome_quality_analyst.utils.definitions import get_raster_dataset
from ohsome_quality_analyst.utils.exceptions import RasterDatasetNotFoundError


class TestRaster(unittest.TestCase):
    def setUp(self):
        self.raster_dataset = get_raster_dataset("GHS_BUILT_R2018A")

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures/heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            self.feature = geojson.load(f)

    @mock.patch(
        "ohsome_quality_analyst.raster.client.get_data_dir",
        return_value="test_dir",
    )
    @mock.patch("os.path.exists", return_value=True)
    def test_get_raster_path(self, *args):
        self.assertEqual(
            raster_client.get_raster_path(self.raster_dataset),
            os.path.join(
                "test_dir", "GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.tif"
            ),
        )

    @mock.patch(
        "ohsome_quality_analyst.raster.client.get_data_dir",
        return_value="test_dir",
    )
    @mock.patch("os.path.exists", return_value=False)
    def test_get_raster_path_error(self, *args):
        self.assertRaises(
            RasterDatasetNotFoundError,
            raster_client.get_raster_path,
            self.raster_dataset,
        )

    @mock.patch(
        "ohsome_quality_analyst.raster.client.get_raster_path",
        return_value=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "GHS_BUILT_R2018A-Heidelberg.tif",
        ),
    )
    def test_get_zonal_stats(self, *args):
        expected = {
            "count": 2,
            "max": 73.3844985961914,
            "mean": 70.12319946289062,
            "min": 66.86190032958984,
        }
        result = raster_client.get_zonal_stats(
            self.feature,
            self.raster_dataset,
        )
        self.assertEqual(expected, result[0])

    def test_transform_different_crs(self):
        expected = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        (664903.2658458926, 5810944.6089190915),
                        (666571.1021172021, 5810944.6089190915),
                        (666474.5092985737, 5812131.278240253),
                        (664806.9147134189, 5812131.278240253),
                        (664903.2658458926, 5810944.6089190915),
                    ]
                ],
            },
            "properties": {},
        }
        result = raster_client.transform(self.feature, self.raster_dataset)
        self.assertDictEqual(expected, result)
        self.assertNotEqual(self.feature, result)

    def test_transform_same_crs(self):
        raster_dataset = get_raster_dataset("VNL")
        result = raster_client.transform(self.feature, raster_dataset)
        self.assertDictEqual(self.feature, result)
