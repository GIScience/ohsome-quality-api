import datetime
import unittest
from pathlib import Path

import numpy as np

from ohsome_quality_analyst.definitions import load_metadata
from ohsome_quality_analyst.indicators.mapping_saturation import models
from ohsome_quality_analyst.indicators.minimal.indicator import (
    Minimal as MinimalIndicator,
)
from ohsome_quality_analyst.reports.minimal.report import Minimal as MinimalReport
from ohsome_quality_analyst.utils.helper import (
    camel_to_hyphen,
    flatten_sequence,
    get_class_from_key,
    get_project_root,
    hyphen_to_camel,
    hyphen_to_snake,
    json_serialize,
    snake_to_camel,
    snake_to_hyphen,
    snake_to_lower_camel,
)

from .mapping_saturation import fixtures


class TestHelper(unittest.TestCase):
    def test_name_to_class(self):
        self.assertIs(
            get_class_from_key(class_type="indicator", key="minimal"),
            MinimalIndicator,
        )

        self.assertIs(
            get_class_from_key(class_type="report", key="minimal"),
            MinimalReport,
        )

        self.indicators = load_metadata("indicators")
        for indicator_name in self.indicators.keys():
            self.assertIsNotNone(
                get_class_from_key(class_type="indicator", key=indicator_name)
            )

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

    def test_camel_to_hyphen(self):
        assert camel_to_hyphen("CamelCase") == "camel-case"

    def test_snake_to_camel(self):
        assert snake_to_camel("snake_case") == "SnakeCase"

    def test_snake_to_lower_camel(self):
        assert snake_to_lower_camel("snake_case") == "snakeCase"

    def test_snake_to_hyphen(self):
        assert snake_to_hyphen("snake_case") == "snake-case"

    def test_hyphen_to_camel(self):
        assert hyphen_to_camel("hyphen-case") == "HyphenCase"

    def test_hyphen_to_snake(self):
        assert hyphen_to_snake("hyphen-case") == "hyphen_case"


if __name__ == "__main__":
    unittest.main()
