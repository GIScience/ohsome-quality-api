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

    def test_base_indicator_valid(self):
        request_models.BaseIndicator(name="minimal")
        request_models.BaseIndicator(
            name="minimal",
            include_svg=True,
            include_html=True,
            include_data=False,
            flatten=False,
        )

    def test_base_indicator_invalid(self):
        with self.assertRaises(ValueError):
            request_models.BaseIndicator()
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(name="foo")
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(includeSvg=True)
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(name="minimal", include_svg="foo")
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(name="minimal", include_html="foo")
        with self.assertRaises(ValueError):
            request_models.BaseIndicator(name="minimal", flatten="foo")

    def test_base_report_valid(self):
        request_models.BaseReport(name="minimal")
        request_models.BaseReport(
            name="minimal",
            include_svg=True,
            include_html=True,
            include_data=False,
            flatten=False,
        )

    def test_base_report_invalid(self):
        with self.assertRaises(ValueError):
            request_models.BaseReport()
        with self.assertRaises(ValueError):
            request_models.BaseReport(name="foo")
        with self.assertRaises(ValueError):
            request_models.BaseReport(include_svg=True)
        with self.assertRaises(ValueError):
            request_models.BaseReport(name="minimal", include_svg="foo")
        with self.assertRaises(ValueError):
            request_models.BaseReport(name="minimal", include_html="foo")
        with self.assertRaises(ValueError):
            request_models.BaseReport(name="minimal", flatten="foo")

    def test_layer_key_valid(self):
        # Test on BaseIndicator because validation of BaseLayer needs indicator name
        request_models.BaseLayerName(layer_key="building_count")

    def test_layer_key_invalid(self):
        # Test on BaseIndicator because validation of BaseLayer needs indicator name
        with self.assertRaises(ValueError):
            request_models.BaseLayerName(layer_key="foo")

    def test_layer_data_valid(self):
        layer = {
            "name": "foo",
            "description": "bar",
            "data": {},
        }
        request_models.BaseLayerData(layer=layer)

    def test_layer_data_invalid(self):
        for layer in (
            {"name": "foo", "data": {}},
            {"description": "bar", "data": {}},
            {"name": "foo", "description": "bar"},
            {"name": "foo", "description": "bar", "data": "fis"},
        ):
            with self.assertRaises(ValueError):
                request_models.BaseLayerData(layer=layer)

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

    def test_bpolys_valid(self):
        request_models.BaseBpolys(bpolys=self.bpolys)

    def test_bpolys_invalid(self):
        bpolys = Polygon(
            [[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.0, 1.0)]]
        )

        with self.assertRaises(ValueError):
            request_models.BaseBpolys(bpolys=bpolys)

    def test_indicator_database(self):
        request_models.IndicatorDatabase(
            name="minimal",
            layer_key="minimal",
            dataset="regions",
            feature_id="3",
        )
        request_models.IndicatorDatabase(
            name="minimal",
            layer_key="minimal",
            dataset="regions",
            feature_id="Heidelberg",
            fid_field="name",
        )

    def test_indicator_bpolys(self):
        request_models.IndicatorBpolys(
            name="minimal",
            layer_key="minimal",
            bpolys=self.bpolys,
        )

    def test_indicator_invalid_layer_combination(self):
        kwargs = {
            "name": "minimal",
            "layer-key": "amenities",
            "dataset": "regions",
            "feature-id": 3,
        }
        with self.assertRaises(ValueError):
            request_models.IndicatorDatabase(**kwargs)
        with self.assertRaises(ValueError):
            request_models.IndicatorBpolys(**kwargs)

    def test_indicator_data(self):
        request_models.IndicatorData(
            name="mapping-saturation",
            bpolys=self.bpolys,
            layer={"name": "foo", "description": "bar", "data": {}},
        )

    def test_indicator_data_invalid_indicator(self):
        with self.assertRaises(ValueError):
            request_models.IndicatorData(
                name="foo",
                bpolys=self.bpolys,
                layer={"name": "foo", "description": "bar", "data": {}},
            )

    def test_invalid_set_of_arguments(self):
        param_keys = (
            "name",
            "layer-key",
            "dataset",
            "feature-id",
            "fid-field",
            "bpolys",
        )
        param_values = (
            "minimal",
            "minimal",
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
                "name": "minimal",
                "layer-key": "minimal",
                "dataset": "regions",
                "feature-id": "3",
            },
            {
                "name": "minimal",
                "layer-key": "minimal",
                "dataset": "regions",
                "feature-id": "3",
                "fid-field": "ogc_fid",
            },
            {
                "name": "minimal",
                "layer-key": "minimal",
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
