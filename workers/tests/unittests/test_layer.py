import unittest

from ohsome_quality_analyst.base.layer import BaseLayer, LayerData, LayerDefinition


class TestLayer(unittest.TestCase):
    def test_base_layer(self):
        BaseLayer("name", "description")
        self.assertRaises(TypeError, BaseLayer, "name")
        self.assertRaises(TypeError, BaseLayer, "description")

    def test_layer_definition(self):
        LayerDefinition("name", "description", "endpoint", "filter")
        LayerDefinition("name", "description", "endpoint", "filter", "source")
        LayerDefinition(
            "name", "description", "endpoint", "filter", "source", "filter2"
        )
        self.assertRaises(TypeError, LayerDefinition, ("name", "description"))
        self.assertRaises(TypeError, LayerDefinition, ("endpoint", "filter"))
        self.assertRaises(
            TypeError,
            LayerDefinition,
            ("name", "description", "endpoint"),
        )
        self.assertRaises(TypeError, LayerDefinition, ("name", "description", "filter"))

    def test_layer_data(self):
        LayerData("name", "description", {})
        self.assertRaises(TypeError, LayerData, ("name", "description"))
        self.assertRaises(TypeError, LayerData, {})
        self.assertRaises(TypeError, LayerData, ("name", "description", "data"))
