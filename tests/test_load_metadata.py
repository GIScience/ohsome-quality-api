import unittest

from schema import Schema

from ohsome_quality_tool.indicators.guf_comparison.indicator import GufComparison


class TestReadMetadata(unittest.TestCase):
    def setUp(self):
        self.indicator = GufComparison(dynamic=True)
        self.metadata = self.indicator.load_metadata()
        self.schema = Schema(
            {
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
        )

    def test_validate_schema(self):
        self.schema.validate(self.metadata)  # Print information if validation fails
        self.assertTrue(self.schema.is_valid(self.metadata))


if __name__ == "__main__":
    unittest.main()
