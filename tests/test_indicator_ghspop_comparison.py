import os
import unittest

from ohsome_quality_tool.oqt import get_dynamic_indicator
from ohsome_quality_tool.utils.definitions import Indicators


class TestGhspopComparisonIndicator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = Indicators.GHSPOP_COMPARISON.name

    def test_get_dynamic_indicator(self):
        """Test if dynamic indicator can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        results = get_dynamic_indicator(
            indicator_name=self.indicator_name, infile=infile
        )

        # check if result dict contains the right keys
        self.assertListEqual(
            list(results.keys()), ["data", "quality_level", "description"]
        )


if __name__ == "__main__":
    unittest.main()
