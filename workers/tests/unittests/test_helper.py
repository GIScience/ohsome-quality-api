import datetime
import json
import os
import unittest
from pathlib import Path

import numpy as np
from geojson import Feature, Polygon

from ohsome_quality_analyst.indicators.mapping_saturation import models
from ohsome_quality_analyst.indicators.minimal.indicator import (
    Minimal as MinimalIndicator,
)
from ohsome_quality_analyst.reports.minimal.report import Minimal as MinimalReport
from ohsome_quality_analyst.utils.helper import (
    camel_to_hyphen,
    camel_to_snake,
    flatten_dict,
    flatten_sequence,
    get_project_root,
    json_serialize,
    loads_geojson,
    name_to_class,
    snake_to_lower_camel,
)

from .mapping_saturation import fixtures


def get_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as file:
        return json.load(file)


class TestHelper(unittest.TestCase):
    def run_tests(self, raw: dict, number_of_features: int = 1) -> None:
        i = 0
        for feature in loads_geojson(raw):
            i += 1
            self.assertIsInstance(feature, Feature)
        self.assertEqual(i, number_of_features)

    def test_name_to_class(self):
        self.assertIs(
            name_to_class(class_type="indicator", name="Minimal"),
            MinimalIndicator,
        )

        self.assertIs(
            name_to_class(class_type="report", name="Minimal"),
            MinimalReport,
        )

    def test_loads_geojson_geometry(self):
        raw = get_fixture("heidelberg-altstadt-geometry.geojson")
        self.run_tests(raw)

    def test_loads_geojson_feature(self):
        raw = get_fixture("heidelberg-altstadt-feature.geojson")
        self.run_tests(raw)

    def test_loads_geojson_featurecollection(self):
        raw = get_fixture("featurecollection.geojson")
        self.run_tests(raw, number_of_features=2)

    def test_loads_geojson_featurecollection_single_feature(self):
        raw = get_fixture("heidelberg-altstadt-featurecollection.geojson")
        self.run_tests(raw)

    def test_loads_geojson_invalid_geometry_type(self):
        raw = get_fixture("line-string.geojson")
        with self.assertRaises(ValueError):
            for _ in loads_geojson(raw):
                pass

    def test_loads_geojson_invalid_geojson(self):
        polygon = Polygon(
            [[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.0, 1.0)]]
        )
        with self.assertRaises(ValueError):
            for _ in loads_geojson(polygon):
                pass

    def test_flatten_dict(self):
        deep = {"foo": {"bar": "baz", "lang": {"нет": "tak"}}, "something": 5}
        flat = {"foo.bar": "baz", "foo.lang.нет": "tak", "something": 5}
        self.assertDictEqual(flatten_dict(deep), flat)

    def test_flatten_dict_list(self):
        deep = {"foo": {"bar": "baz", "lang": {"нет": ["tak", "tak2"]}}, "something": 5}
        flat = {
            "foo.bar": "baz",
            "foo.lang.нет.0": "tak",
            "foo.lang.нет.1": "tak2",
            "something": 5,
        }
        self.assertDictEqual(flatten_dict(deep), flat)

    def test_flatten_dict_list_nested(self):
        deep = {
            "foo": {
                "bar": "baz",
                "lang": {
                    "нет": [
                        {"tak": {"taktak": "taktaktak"}},
                        {"tok": {"toktok": "toktoktok"}},
                    ]
                },
            },
            "something": 5,
        }
        flat = {
            "foo.bar": "baz",
            "foo.lang.нет.0.tak.taktak": "taktaktak",
            "foo.lang.нет.1.tok.toktok": "toktoktok",
            "something": 5,
        }
        self.assertDictEqual(flatten_dict(deep), flat)

    def test_flatten_dict_list_nested_2(self):
        deep = {
            "foo": {
                "bar": "baz",
                "lang": {
                    "нет": [
                        [
                            {"tak": "taktak"},
                            {"tok": "toktok"},
                        ],
                        [
                            {"tak2": "taktak2"},
                            {"tok2": "toktok2"},
                        ],
                    ]
                },
            },
            "something": 5,
        }
        flat = {
            "foo.bar": "baz",
            "foo.lang.нет.0.0.tak": "taktak",
            "foo.lang.нет.0.1.tok": "toktok",
            "foo.lang.нет.1.0.tak2": "taktak2",
            "foo.lang.нет.1.1.tok2": "toktok2",
            "something": 5,
        }
        self.assertDictEqual(flatten_dict(deep), flat)

    # TODO: add tests for other input than dict
    def test_flatten_seq(self):
        input_seq = {
            "regions": {"default": "ogc_fid"},
            "gadm": {
                "default": "uid",  # ISO 3166-1 alpha-3 country code
                "other": (("name_1", "name_2"), ("id_1", "id_2")),
            },
        }
        output_seq = ["ogc_fid", "uid", "name_1", "name_2", "id_1", "id_2"]
        self.assertListEqual(flatten_sequence(input_seq), output_seq)

    def test_json_serialize_valid_input_datetime(self):
        self.assertIsInstance(json_serialize(datetime.datetime.now()), str)

    def test_json_serialize_valid_input_date(self):
        self.assertIsInstance(json_serialize(datetime.date.today()), str)

    def test_json_serialize_valid_input_np_float(self):
        np_float = np.array([1.1])[0]
        self.assertIsInstance(json_serialize(np_float), float)

    def test_json_serialize_valid_input_np_int(self):
        np_int = np.array([1])[0]
        self.assertIsInstance(json_serialize(np_int), int)

    def test_json_serialize_valid_input_fit(self):
        ydata = fixtures.VALUES_1
        xdata = np.array(range(len(ydata)))
        self.assertIsInstance(json_serialize(models.SSlogis(xdata, ydata)), dict)

    def test_json_serialize_invalid_input(self):
        with self.assertRaises(TypeError):
            json_serialize("foo")

    def test_get_project_root(self):
        expected = Path(__file__).resolve().parent.parent.parent.resolve()
        result = get_project_root()
        self.assertEqual(expected, result)

    def test_camel_to_snake(self):
        assert camel_to_snake("CamelCase") == "camel_case"

    def test_camel_to_lower_hyphen(self):
        assert camel_to_hyphen("CamelCase") == "camel-case"

    def test_snake_to_lower_camel(self):
        assert snake_to_lower_camel("snake_case") == "snakeCase"


if __name__ == "__main__":
    unittest.main()
