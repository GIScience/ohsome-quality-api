import unittest

from schema import Schema

from ohsome_quality_tool.utils.definitions import (
    get_indicator_metadata,
    load_indicator_metadata,
)


class TestReadMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = load_indicator_metadata()
        self.schema = Schema(
            {
                str: {
                    "name": str,
                    "indicator_description": str,
                    "label_description": {
                        "red": str,
                        "yellow": str,
                        "green": str,
                        "undefined": str,
                    },
                    "result_description": str,
                }
            }
        )

    def test_validate_schema(self):
        self.schema.validate(self.metadata)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(self.metadata))

    def test_get_indicator_metadata(self):
        self.assertRaises(KeyError, get_indicator_metadata, "")
        self.assertRaises(KeyError, get_indicator_metadata, "ajsjdh")
        self.assertRaises(KeyError, get_indicator_metadata, None)
        self.assertIsInstance(get_indicator_metadata("GufComparison"), dict)


if __name__ == "__main__":
    unittest.main()
