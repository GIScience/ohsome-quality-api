"""Test module for the `pydantic` data models for API requests"""
import itertools
import json
import os
import unittest

from geojson import Polygon

from ohsome_quality_analyst.api import request_models


class TestApiRequestModels(unittest.TestCase):
    def setUp(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as file:
            self.bpolys = json.load(file)

    def test_bpolys_valid(self):
        request_models.BaseBpolys(bpolys=self.bpolys)

    def test_bpolys_invalid(self):
        bpolys = Polygon(
            [[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.0, 1.0)]]
        )

        with self.assertRaises(ValueError):
            request_models.BaseBpolys(bpolys=bpolys)

    def test_dataset_valid(self):
        request_models.BaseDatabase(dataset="regions", feature_id="3")
        request_models.BaseDatabase(
            dataset="regions", feature_id="3", fid_field="ogc_fid"
        )
        request_models.BaseDatabase(dataset="regions", feature_id="3")
        request_models.BaseDatabase(
            dataset="regions", feature_id="3", fid_field="ogc_fid"
        )

    def test_dataset_invalid(self):
        with self.assertRaises(ValueError):
            request_models.BaseDatabase(dataset="foo", feature_id="3")
        with self.assertRaises(ValueError):
            request_models.BaseDatabase(dataset="foo", feature_id="3")

    def test_valid_layer(self):
        request_models.BaseIndicator(
            name="GhsPopComparisonBuildings",
            layerName="building_count",
        )

    def test_invalid_layer(self):
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(
                name="GhsPopComparisonBuildings",
                layerName="foo",
            )

    def test_invalid_indicator_layer_combination(self):
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(
                name="GhsPopComparisonBuildings",
                layerName="amenities",
            )

    def test_indicator_database(self):
        request_models.IndicatorDatabase(
            name="GhsPopComparisonBuildings",
            layerName="building_count",
            dataset="regions",
            featureId="3",
        )
        request_models.IndicatorDatabase(
            name="GhsPopComparisonBuildings",
            layerName="building_count",
            dataset="regions",
            featureId="Heidelberg",
            fidField="name",
        )

    def test_indicator_bpolys(self):
        request_models.IndicatorBpolys(
            name="GhsPopComparisonBuildings",
            layerName="building_count",
            bpolys=self.bpolys,
        )

    def test_invalid_set_of_arguments(self):
        param_keys = (
            "name",
            "layerName",
            "dataset",
            "featureId",
            "fidField",
            "bpolys",
        )
        param_values = (
            "GhsPopComparisonBuildings",
            "building_count",
            "regions",
            "3",
            "ogc_fid",
            "bpolys",
        )
        all_combinations = []
        for i, _ in enumerate(param_keys):
            for key_comb, val_comb in zip(
                itertools.combinations(param_keys, i),
                itertools.combinations(param_values, i),
            ):
                all_combinations.append(
                    {key: value for key, value in zip(key_comb, val_comb)}
                )
        valid_combinations = (
            {
                "name": "GhsPopComparisonBuildings",
                "layerName": "building_count",
                "dataset": "regions",
                "featureId": "3",
            },
            {
                "name": "GhsPopComparisonBuildings",
                "layerName": "building_count",
                "dataset": "regions",
                "featureId": "3",
                "fidField": "ogc_fid",
            },
            {
                "name": "GhsPopComparisonBuildings",
                "layerName": "building_count",
                "bpolys": self.bpolys,
            },
        )
        for combination in all_combinations:
            if combination in valid_combinations:
                continue
            for model in (
                request_models.IndicatorBpolys,
                request_models.IndicatorDatabase,
            ):
                with self.assertRaises(ValueError):
                    model(**combination)
