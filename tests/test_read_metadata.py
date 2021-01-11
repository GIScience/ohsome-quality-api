import unittest

from schema import Or, Schema

from ohsome_quality_tool.indicators.guf_comparison.indicator import GufComparison


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.metadata = GufComparison(dynamic=True, bpolys="").read_metadata()
        self.schema = Schema(
            {
                "name": str,
                "description": str,
                "label_interpretation": {
                    "red": {"threshold": Or(float, int), "description": str},
                    "yellow": {"threshold": Or(float, int), "description": str},
                    "green": {"threshold": Or(float, int), "description": str},
                    "undefined": {"threshold": None, "description": str},
                },
            }
        )

    def test_validate_schema(self):
        # self.schema.validate(self.metadata)  # Print information about validation
        self.assertTrue(self.schema.is_valid(self.metadata))


if __name__ == "__main__":
    unittest.main()
