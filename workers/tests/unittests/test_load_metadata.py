import unittest

from schema import Schema

from ohsome_quality_analyst.definitions import get_metadata, load_metadata


class TestReadMetadata(unittest.TestCase):
    def test_validate_indicator_schema(self):
        schema = Schema(
            {
                str: {
                    "name": str,
                    "description": str,
                    "label-description": {
                        "red": str,
                        "yellow": str,
                        "green": str,
                        "undefined": str,
                    },
                    "result-description": str,
                }
            }
        )
        metadata = load_metadata("indicators")
        schema.validate(metadata)  # Print information if validation fails
        self.assertTrue(schema.is_valid(metadata))

    def test_validate_report_schema(self):
        schema = Schema(
            {
                str: {
                    "name": str,
                    "description": str,
                    "label-description": {
                        "red": str,
                        "yellow": str,
                        "green": str,
                        "undefined": str,
                    },
                }
            }
        )
        metadata = load_metadata("reports")
        schema.validate(metadata)  # Print information if validation fails
        self.assertTrue(schema.is_valid(metadata))

    def test_get_indicator_metadata(self):
        self.assertRaises(ValueError, get_metadata, "", "")
        self.assertRaises(KeyError, get_metadata, "indicators", "ajsjdh")
        self.assertIsInstance(get_metadata("indicators", "Minimal"), dict)

    def test_get_report_metadata(self):
        self.assertRaises(ValueError, get_metadata, "", "")
        self.assertRaises(KeyError, get_metadata, "reports", "ajsjdh")
        self.assertIsInstance(get_metadata("reports", "Minimal"), dict)


if __name__ == "__main__":
    unittest.main()
