import unittest

from ohsome_quality_tool.indicators.guf_comparison.indicator import Indicator


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        # TODO: Test if dict is of schema.
        indicator = Indicator(dynamic=True, bpolys="")
        result = indicator.read_metadata()

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result.keys()), 1)

        for key, value in result.items():
            for k in ("name", "description", "label_interpretation"):
                self.assertIn(k, value.keys())


if __name__ == "__main__":
    unittest.main()
