import pytest

from ohsome_quality_api.attributes import definitions
from ohsome_quality_api.attributes.models import Attribute


@pytest.fixture()
def attribute_key_string():
    return "height"


def test_get_attributes():
    atbs = definitions.get_attributes()
    assert isinstance(atbs, dict)
    for key, value in atbs.items():
        for k, v in value.items():
            assert isinstance(k, str)
            assert isinstance(v, Attribute)


def test_get_attribute(attribute_key_string, topic_key_building_count):
    atb = definitions.get_attribute(topic_key_building_count, attribute_key_string)
    assert isinstance(atb, Attribute)


def test_get_attribute_wrong_key():
    with pytest.raises(KeyError):
        definitions.get_attribute("foo", "bar")


def test_build_attribute_filter(attribute_key, topic_key_building_count):
    atb = definitions.build_attribute_filter(attribute_key, topic_key_building_count)
    assert isinstance(atb, str)


def test_build_attribute_filter_multiple_attributes(
    attribute_key_multiple, topic_key_building_count
):
    atb = definitions.build_attribute_filter(
        attribute_key_multiple, topic_key_building_count
    )
    assert isinstance(atb, str)


def test_build_attribute_filter_wrong_key():
    with pytest.raises(KeyError):
        definitions.build_attribute_filter("foo", "bar")


def test_get_attribute_preset(topic_key_building_count):
    atb = definitions.get_attribute_preset(topic_key_building_count)
    assert isinstance(atb, dict)
    for key, value in atb.items():
        assert isinstance(value, Attribute)
