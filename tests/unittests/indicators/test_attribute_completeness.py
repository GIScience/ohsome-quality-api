from unittests.utils import get_topic_fixture

from ohsome_quality_api.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)


def test_create_description():
    def topic_building_count():  # for getting an object with the attribute "name"
        pass

    indicator = AttributeCompleteness(
        topic_building_count,
        "feature",
        "attribute_key",
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.topic.name = "test-topic"
    indicator.attribute_key = ["test-attribute"]
    indicator.create_description()
    assert indicator.description == (
        "The ratio of the topic test-topic in "
        "the selected area (all: 10) compared to the "
        "topic test-topic with the expected tag test-attribute (matched: 2) is 0.2. "
    )


def test_create_description_multiple_attributes():
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        "building_count",
        ["height", "house-number", "address-street"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    assert indicator.description == (
        "The ratio of the topic building count in the selected area (all: 10 elements)"
        " compared to the topic building count with the expected attributes height of"
        " buildings, house number, street address (matched: 2 elements) is 0.2. "
    )
