import pytest
from pytest_approval.main import verify

from ohsome_quality_api.attributes import definitions
from ohsome_quality_api.attributes.models import Attribute


@pytest.fixture()
def attribute_key_string():
    return "height"


def test_get_attributes():
    attributes = definitions.get_attributes()
    assert isinstance(attributes, dict)
    for value in attributes.values():
        for k, v in value.items():
            assert isinstance(k, str)
            assert isinstance(v, Attribute)


def test_get_attribute(attribute_key_string, topic_key_building_count):
    attribute = definitions.get_attribute(
        topic_key_building_count, attribute_key_string
    )
    assert isinstance(attribute, Attribute)


def test_get_attribute_wrong_key():
    with pytest.raises(KeyError):
        definitions.get_attribute("foo", "bar")


def test_build_attribute_filter(attribute_key, topic_key_building_count):
    attribute = definitions.build_attribute_filter(
        attribute_key, topic_key_building_count
    )
    assert isinstance(attribute, str)
    assert (
        attribute == "building=* and building!=no and geometry:polygon"
        " and (height=* or building:levels=*)"
    )


def test_build_attribute_filter_multiple_attributes(
    attribute_key_multiple, topic_key_building_count
):
    attribute = definitions.build_attribute_filter(
        attribute_key_multiple, topic_key_building_count
    )
    assert isinstance(attribute, str)


def test_build_attribute_filter_wrong_key():
    with pytest.raises(KeyError):
        definitions.build_attribute_filter("foo", "bar")


def test_get_attribute_preset(topic_key_building_count):
    attribute = definitions.get_attribute_preset(topic_key_building_count)
    assert isinstance(attribute, dict)
    for value in attribute.values():
        assert isinstance(value, Attribute)


def test_get_attribute_translated(
    topic_key_building_count, attribute_key_string, locale_de
):
    attribute = definitions.get_attribute(
        topic_key_building_count, attribute_key_string
    )
    assert verify(attribute.model_dump_json(indent=2))
