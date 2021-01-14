import unittest

from ohsome_quality_tool.indicators.guf_comparison.indicator import GufComparison


class TestReadMetadata(unittest.TestCase):
    def setUp(self):
        self.indicator = GufComparison(dynamic=True, bpolys="")

    def test_validate_schema(self):
        self.indicator.set_layer_definition("building_area")


if __name__ == "__main__":
    unittest.main()
