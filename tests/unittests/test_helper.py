import datetime
from pathlib import Path

import numpy as np
import pytest

from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.indicators.definitions import get_indicator_metadata
from ohsome_quality_api.indicators.mapping_saturation import models
from ohsome_quality_api.indicators.minimal.indicator import Minimal
from ohsome_quality_api.utils.helper import (
    camel_to_hyphen,
    get_class_from_key,
    get_module_dir,
    get_project_root,
    hyphen_to_camel,
    hyphen_to_snake,
    json_serialize,
    snake_to_camel,
    snake_to_hyphen,
    snake_to_lower_camel,
)
from ohsome_quality_api.utils.pybabel_yaml_extractor import flatten_sequence

from .mapping_saturation import fixtures


def test_name_to_class():
    assert get_class_from_key(class_type="indicator", key="minimal") == Minimal

    indicators = get_indicator_metadata()
    for indicator_name in indicators:
        assert issubclass(
            get_class_from_key(class_type="indicator", key=indicator_name),
            BaseIndicator,
        )


# TODO: add tests for other input than dict
def test_flatten_seq():
    input_seq = {
        "regions": {"default": "ogc_fid"},
        "gadm": {
            "default": "uid",  # ISO 3166-1 alpha-3 country code
            "other": (("name_1", "name_2"), ("id_1", "id_2")),
        },
    }
    output_seq = ["ogc_fid", "uid", "name_1", "name_2", "id_1", "id_2"]
    assert flatten_sequence(input_seq) == output_seq


def test_json_serialize_valid_input_datetime():
    assert isinstance(json_serialize(datetime.datetime.now()), str)


def test_json_serialize_valid_input_date():
    assert isinstance(json_serialize(datetime.date.today()), str)


def test_json_serialize_valid_input_np_float():
    np_float = np.array([1.1])[0]
    assert isinstance(json_serialize(np_float), float)


def test_json_serialize_valid_input_np_int():
    np_int = np.array([1])[0]
    assert isinstance(json_serialize(np_int), int)


def test_json_serialize_valid_input_fit():
    ydata = fixtures.VALUES_1
    xdata = np.array(range(len(ydata)))
    assert isinstance(json_serialize(models.SSlogis(xdata, ydata)), dict)


def test_json_serialize_invalid_input():
    with pytest.raises(TypeError):
        json_serialize("foo")


def test_get_project_root():
    expected = Path(__file__).resolve().parent.parent.parent.resolve()
    result = get_project_root()
    assert expected == result


def test_camel_to_hyphen():
    assert camel_to_hyphen("CamelCase") == "camel-case"


def test_snake_to_camel():
    assert snake_to_camel("snake_case") == "SnakeCase"


def test_snake_to_lower_camel():
    assert snake_to_lower_camel("snake_case") == "snakeCase"


def test_snake_to_hyphen():
    assert snake_to_hyphen("snake_case") == "snake-case"


def test_hyphen_to_camel():
    assert hyphen_to_camel("hyphen-case") == "HyphenCase"


def test_hyphen_to_snake():
    assert hyphen_to_snake("hyphen-case") == "hyphen_case"


def test_get_module_dir():
    assert get_module_dir("tests.unittests") == str(Path(__file__).parent)
