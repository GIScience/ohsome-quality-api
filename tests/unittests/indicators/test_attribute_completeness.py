from ohsome_quality_api.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)


def test_create_description():
    def topic_building_count():
        pass

    indicator = AttributeCompleteness(
        topic_building_count,
        "feature_germany_heidelberg",
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
        'topic test-topic with the expected tag "test-attribute" (matched: 2) is 0.2. '
    )
