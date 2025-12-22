import pytest
from pydantic import ValidationError

from ohsome_quality_api.topics.models import BaseTopic, Topic, TopicData


def test_base_topic():
    BaseTopic(key="key", name="name", description="description")


def test_base_topic_missing():
    with pytest.raises(ValidationError):
        BaseTopic(key="key")
        BaseTopic(name="name")
        BaseTopic(description="description")


def test_base_topic_extra():
    with pytest.raises(ValidationError):
        BaseTopic(name="name", key="key", description="description", foo="bar")


def test_topic_definition():
    Topic(
        key="key",
        name="name",
        description="description",
        indicators=["mapping-saturation"],
        projects=["core"],
        endpoint="elements",
        aggregation_type="count",
        filter="filter",
    )
    Topic(
        key="key",
        name="name",
        description="description",
        indicators=["mapping-saturation"],
        projects=["core"],
        endpoint="elements",
        aggregation_type="count",
        filter="filter",
        source="source",
    )
    Topic(
        key="key",
        name="name",
        description="description",
        indicators=["mapping-saturation", "minimal"],
        projects=["core"],
        endpoint="elements",
        aggregation_type="count",
        filter="filter",
        source="source",
    )
    Topic(
        key="key",
        name="name",
        description="description",
        indicators=["mapping-saturation", "minimal"],
        projects=["core", "experimental"],
        endpoint="elements",
        aggregation_type="count",
        filter="filter",
        source="source",
    )
    Topic(
        key="key",
        name="name",
        description="description",
        indicators=[],
        projects=["core"],
        endpoint="elements",
        aggregation_type="count",
        filter="filter",
        source="source",
    )
    Topic(
        key="key",
        name="name",
        description="description",
        indicators=["mapping-saturation"],
        projects=["core"],
        endpoint="elements",
        aggregation_type="count",
        filter="filter",
        source="source",
        ratio_filter="ration_filter",
    )


def test_topic_definition_missing():
    with pytest.raises(ValidationError):
        Topic(key="key", name="name", description="description")


def test_topic_definition_extra():
    with pytest.raises(ValidationError):
        Topic(
            key="key",
            name="name",
            description="description",
            projects=["core"],
            endpoint="elements",
            filter="filter",
            foo="bar",
        )


def test_topic_data():
    TopicData(key="key", name="name", description="description", data={})


def test_topic_missing():
    with pytest.raises(ValidationError):
        TopicData(key="key", name="name", description="description")


def test_topic_extra():
    with pytest.raises(ValidationError):
        TopicData(key="key", name="name", description="description", data={}, foo="bar")
