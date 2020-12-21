import unittest

from schema import Schema

from ohsome_quality_tool.indicators.guf_comparison.indicator import Indicator


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.metadata = Indicator(dynamic=True, bpolys="").read_metadata()
        self.schema = Schema(
            [{"id": {"name": str, "description": str, "label_interpretation": dict}}]
        )

    def test_upper(self):
        # TODO: Test if dict is of schema.
        print(self.metadata)

        self.assertIsInstance(self.metadata, dict)
        self.assertEqual(len(self.metadata.keys()), 1)

        for key, value in self.metadata.items():
            for k in ("name", "description", "label_interpretation"):
                self.assertIn(k, value.keys())

    def validate_schema(self):
        self.schema.is_valid(self.metadata)


if __name__ == "__main__":
    unittest.main()
