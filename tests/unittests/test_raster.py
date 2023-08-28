import json
import os
import tempfile
import unittest
from unittest import mock

from geojson_pydantic import Feature

import ohsome_quality_analyst.raster.client as raster_client
from ohsome_quality_analyst.raster.definitions import get_raster_dataset
from ohsome_quality_analyst.utils.exceptions import RasterDatasetNotFoundError


class TestRaster(unittest.TestCase):
    def setUp(self):
        self.raster_dataset = get_raster_dataset("GHS_BUILT_R2018A")
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures/heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as f:
            self.feature = Feature(**json.load(f))

    def test_get_raster_path(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            path = os.path.join(
                tmpdirname,
                "GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.tif",
            )
            with open(path, "w") as f:
                f.write("")
            with mock.patch(
                "ohsome_quality_analyst.raster.client.get_config_value",
                return_value=tmpdirname,
            ):
                self.assertEqual(
                    raster_client.get_raster_path(self.raster_dataset),
                    path,
                )

    @mock.patch("ohsome_quality_analyst.raster.client.os")
    def test_get_raster_path_error(self, mock_os):
        mock_os.path.exists.return_value = False
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
        expected = [
            {
                "count": 2,
                "max": 73.3844985961914,
                "mean": 70.12319946289062,
                "min": 66.86190032958984,
            }
        ]
        result = raster_client.get_zonal_stats(
            self.feature,
            self.raster_dataset,
        )
        self.assertEqual(expected, result)

    @mock.patch(
        "ohsome_quality_analyst.raster.client.get_raster_path",
        return_value=os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "nodata.tif",
        ),
    )
    def test_get_zonal_stats_nodata(self, *args):
        """Test on a raster file with only pixel values of -222 (nodata)"""
        expected = [{"count": 0, "sum": None}]
        result = raster_client.get_zonal_stats(
            self.feature, self.raster_dataset, stats=["count", "sum"]
        )
        self.assertEqual(expected, result)

    def test_transform_different_crs(self):
        expected = Feature(
            **{
                "bbox": None,
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            (664903.2842561695, 5810944.658597255),
                            (666571.1266135585, 5810944.658597255),
                            (666474.5362297115, 5812131.297943545),
                            (664806.9355532578, 5812131.297943545),
                            (664903.2842561695, 5810944.658597255),
                        ]
                    ],
                },
                "properties": {},
                "id": None,
            }
        )
        result = raster_client.transform(self.feature, self.raster_dataset)
        self.assertDictEqual(expected.model_dump(), result.model_dump())
        self.assertNotEqual(self.feature, result)

    def test_transform_same_crs(self):
        raster_dataset = get_raster_dataset("VNL")
        result = raster_client.transform(self.feature, raster_dataset)
        self.assertDictEqual(self.feature.model_dump(), result.model_dump())
