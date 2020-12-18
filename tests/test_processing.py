import os
import unittest

from ohsome_quality_tool.oqt import process_indicator


class TestPoiDensityIndicator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = "ghspop-comparison"
        self.dataset_name = "test-regions"
        self.layer_name = "building-count"

    def test_process_indicator(self):
        """Test if dynamic indicator can be calculated."""

        process_indicator(
            indicator_name=self.indicator_name,
            dataset=self.dataset_name,
            layer_name=self.layer_name,
            only_missing_ids=False,
        )

        # check if result dict contains the right keys
        # self.assertListEqual(list(result._fields), ["label", "value", "text", "svg"])


if __name__ == "__main__":
    unittest.main()
