"""Test module for the `pydantic` data models for API requests"""

import os
import unittest

from ohsome_quality_analyst.api import request_models


class TestApiRequestModels(unittest.TestCase):
    def setUp(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as file:
            self.bpolys = file.read()

    def test_bpolys_valid(self):
        request_models.BaseRequestModel(bpolys=self.bpolys)

    def test_bpolys_invalid(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "ohsome-response-200-invalid.geojson",
        )
        with open(path, "r") as file:
            bpolys = file.read()

        with self.assertRaises(ValueError):
            request_models.BaseRequestModel(bpolys=bpolys)

    def test_dataset_valid(self):
        request_models.BaseRequestModel(dataset="regions", feature_id="3")
        request_models.BaseRequestModel(
            dataset="regions", feature_id="3", fid_field="ogc_fid"
        )

    def test_dataset_invalid(self):
        with self.assertRaises(ValueError):
            request_models.BaseRequestModel(dataset="foo", feature_id="3")

    def test_invalid_set_of_arguments(self):
        with self.assertRaises(ValueError):
            request_models.BaseRequestModel(
                bpolys=self.bpolys, dataset="regions", feature_id="3"
            )
        with self.assertRaises(ValueError):
            request_models.BaseRequestModel(dataset="regions")
        with self.assertRaises(ValueError):
            request_models.BaseRequestModel(feature_id="3")
