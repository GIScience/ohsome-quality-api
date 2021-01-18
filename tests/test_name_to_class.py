import unittest

from ohsome_quality_tool.indicators.ghs_pop_comparison.indicator import GhsPopComparison
from ohsome_quality_tool.utils.definitions import load_indicator_metadata
from ohsome_quality_tool.utils.helper import name_to_class


class TestNameToClass(unittest.TestCase):
    def setUp(self):
        self.class_name = "GhsPopComparison"
        self.indicators = load_indicator_metadata()

    def test(self):
        self.assertIs(name_to_class(self.class_name), GhsPopComparison)

    def test_all_indicators(self):
        for indicator in self.indicators.keys():
            self.assertIsNotNone(name_to_class(indicator))


if __name__ == "__main__":
    unittest.main()
