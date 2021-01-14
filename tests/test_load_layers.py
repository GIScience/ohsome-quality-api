import unittest

from schema import Schema

from ohsome_quality_tool.ohsome.client import load_layer_definitions


class TestLoadLayers(unittest.TestCase):
    def setUp(self):
        self.layers = load_layer_definitions()
        self.schema = Schema(
            {str: {"name": str, "description": str, "endpoint": str, "filter": str}}
        )

    def test_validate_schema(self):
        self.schema.validate(self.layers)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(self.layers))


if __name__ == "__main__":
    unittest.main()
