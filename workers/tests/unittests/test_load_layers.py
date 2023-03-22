import unittest

from schema import Optional, Or, Schema

from ohsome_quality_analyst.base.topic import TopicDefinition
from ohsome_quality_analyst.definitions import (
    get_topic_definition,
    load_topic_definitions,
)


class TestLoadLayers(unittest.TestCase):
    def setUp(self):
        self.layers = load_topic_definitions()
        self.schema = Schema(
            {
                str: {
                    "name": str,
                    "description": str,
                    "endpoint": str,
                    "filter": str,
                    "project": str,
                    Optional("ratio_filter", default=None): Or(str, None),
                    Optional("source", default=None): Or(str, None),
                }
            }
        )

    def test_validate_schema(self):
        self.schema.validate(self.layers)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(self.layers))

    def test_get_layer_definition(self):
        self.assertRaises(KeyError, get_topic_definition, "")
        self.assertRaises(KeyError, get_topic_definition, "ajsjdh")
        self.assertRaises(KeyError, get_topic_definition, None)
        self.assertIsInstance(get_topic_definition("building_area"), TopicDefinition)


if __name__ == "__main__":
    unittest.main()
