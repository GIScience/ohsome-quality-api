import pytest
import yaml

from ohsome_quality_api.utils.pybabel_yaml_extractor import (
    filter_dictonary_by_keys,
    flatten_sequence,
    pybabel_yaml_extractor,
)


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


def test_filter_dictonary_by_keys():
    input_seq = {
        "regions": {"default": "ogc_fid"},
        "gadm": {
            "default": "uid",  # ISO 3166-1 alpha-3 country code
            "other": (("name_1", "name_2"), ("id_1", "id_2")),
        },
    }
    output = filter_dictonary_by_keys(input_seq, ["other"])
    assert output == {"gadm": {"other": (("name_1", "name_2"), ("id_1", "id_2"))}}


def test_no_keys(tmp_path):
    path = tmp_path / "foo.yaml"
    with open(path, "w") as file:
        file.write(
            yaml.dump(
                {
                    "name": "Silenthand Olleander",
                    "race": "Human",
                    "traits": ["ONE_HAND", "ONE_EYE"],
                }
            )
        )
    options = {}
    with open(path, "r") as file, pytest.raises(ValueError):
        list(pybabel_yaml_extractor(file, None, None, options))


def test_flat(tmp_path):
    path = tmp_path / "foo.yaml"
    with open(path, "w") as file:
        file.write(
            yaml.dump(
                {
                    "name": "Silenthand Olleander",
                    "race": "Human",
                    "traits": ["ONE_HAND", "ONE_EYE"],
                }
            )
        )
    options = {"keys": "name,traits"}
    with open(path, "r") as file:
        result = list(pybabel_yaml_extractor(file, None, None, options))
    assert result == [
        ("", "", "Silenthand Olleander", ""),
        ("", "", "ONE_HAND", ""),
        ("", "", "ONE_EYE", ""),
    ]


def test_nested(tmp_path):
    path = tmp_path / "foo.yaml"
    with open(path, "w") as file:
        file.write(
            yaml.dump(
                {
                    "hero": {
                        "hp": 34,
                        "sp": 8,
                        "level": 4,
                    },
                    "orc": {
                        "hp": 12,
                        "sp": 0,
                        "level": 2,
                    },
                }
            )
        )
    options = {"keys": "hp"}
    with open(path, "r") as file:
        result = list(pybabel_yaml_extractor(file, None, None, options))
    assert result == [("", "", 34, ""), ("", "", 12, "")]
