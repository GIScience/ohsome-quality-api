import unittest

from ohsome_quality_analyst.base.layer import BaseLayer, LayerData, LayerDefinition


class TestLayer(unittest.TestCase):
    def test_base_layer(self):
        BaseLayer("name", "description")
        self.assertRaises(TypeError, BaseLayer, "name")
        self.assertRaises(TypeError, BaseLayer, "description")

    def test_layer_definition(self):
        LayerDefinition("key", "name", "description", "project", "endpoint", "filter")
        LayerDefinition(
            "key", "name", "description", "project", "endpoint", "filter", "source"
        )
        LayerDefinition(
            "key", "name", "description", "project", "endpoint", "filter", "source"
        )
        LayerDefinition(
            "key",
            "name",
            "description",
            "project",
            "endpoint",
            "filter",
            "source",
            "filter2",
        )
        self.assertRaises(TypeError, LayerDefinition, ("key", "name", "description"))
        self.assertRaises(TypeError, LayerDefinition, ("key", "endpoint", "filter"))
        self.assertRaises(
            TypeError,
            LayerDefinition,
            ("key", "name", "description", "endpoint"),
        )
        self.assertRaises(
            TypeError, LayerDefinition, ("key", "name", "description", "filter")
        )

    def test_layer_data(self):
        LayerData("name", "description", {})
        LayerData("name", "description", {}, key="key")
        self.assertRaises(TypeError, LayerData, ("name", "description"))
        self.assertRaises(TypeError, LayerData, {})
        self.assertRaises(TypeError, LayerData, ("name", "description", "data"))
