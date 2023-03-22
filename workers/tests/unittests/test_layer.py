import pytest
from pydantic import ValidationError

from ohsome_quality_analyst.base.layer import BaseLayer, LayerData, LayerDefinition


def test_base_layer():
    BaseLayer(key="key", name="name", description="description")


def test_base_layer_missing():
    with pytest.raises(ValidationError):
        BaseLayer(key="key")
        BaseLayer(name="name")
        BaseLayer(description="description")


def test_base_layer_extra():
    with pytest.raises(ValidationError):
        BaseLayer(name="name", key="key", description="description", foo="bar")


def test_layer_definition():
    LayerDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
    )
    LayerDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
        source="source",
    )
    LayerDefinition(
        key="key",
        name="name",
        description="description",
        project="core",
        endpoint="endpoint",
        filter_="filter",
        source="source",
    )
    LayerDefinition(
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
        LayerDefinition(key="key", name="name", description="description")


def test_layer_definition_extra():
    with pytest.raises(ValidationError):
        LayerDefinition(
            key="key",
            name="name",
            description="description",
            project="core",
            endpoint="endpoint",
            filter_="filter",
            foo="bar",
        )


def test_layer_data():
    LayerData(key="key", name="name", description="description", data={})


def test_layer_missing():
    with pytest.raises(ValidationError):
        LayerData(key="key", name="name", description="description")


def test_layer_extra():
    with pytest.raises(ValidationError):
        LayerData(key="key", name="name", description="description", data={}, foo="bar")
