import pytest
from pydantic import ValidationError

from ohsome_quality_analyst.base.topic import BaseTopic, TopicData, TopicDefinition


def test_base_layer():
    BaseTopic(key="key", name="name", description="description")


def test_base_layer_missing():
    with pytest.raises(ValidationError):
        BaseTopic(key="key")
        BaseTopic(name="name")
        BaseTopic(description="description")


def test_base_layer_extra():
    with pytest.raises(ValidationError):
        BaseTopic(name="name", key="key", description="description", foo="bar")


def test_layer_definition():
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


def test_layer_definition_missing():
    with pytest.raises(ValidationError):
        TopicDefinition(key="key", name="name", description="description")


def test_layer_definition_extra():
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


def test_layer_data():
    TopicData(key="key", name="name", description="description", data={})


def test_layer_missing():
    with pytest.raises(ValidationError):
        TopicData(key="key", name="name", description="description")


def test_layer_extra():
    with pytest.raises(ValidationError):
        TopicData(key="key", name="name", description="description", data={}, foo="bar")
