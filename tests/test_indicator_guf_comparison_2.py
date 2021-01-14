import unittest

from ohsome_quality_tool.indicators.guf_comparison.indicator import GufComparison


class TestIndicatorGufComparison(unittest.TestCase):
    def setUp(self):
        self.indicator = GufComparison(dynamic=True, bpolys="")


if __name__ == "__main__":
    unittest.main()
