import pytest
from pydantic import ValidationError

from ohsome_quality_analyst.base.topic import BaseTopic, TopicData, TopicDefinition


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
    TopicDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
    )
    TopicDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
        source="source",
    )
    TopicDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
        source="source",
    )
    TopicDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
        source="source",
        ratio_filter="ration_filter",
    )


def test_topic_definition_missing():
    with pytest.raises(ValidationError):
        TopicDefinition(key="key", name="name", description="description")


def test_topic_definition_extra():
    with pytest.raises(ValidationError):
        TopicDefinition(
            key="key",
            name="name",
            description="description",
            project="core",
            endpoint="endpoint",
            filter_="filter",
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