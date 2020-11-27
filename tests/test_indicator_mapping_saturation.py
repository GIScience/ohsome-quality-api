import os
import unittest

from ohsome_quality_tool.oqt import get_dynamic_indicator
from ohsome_quality_tool.utils.definitions import Indicators


class TestMappingSaturationIndicator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.indicator_name = Indicators.MAPPING_SATURATION.name

    def test_get_dynamic_indicator(self):
        """Test if dynamic indicator can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/antanarivo.geojson")
        result, metadata = get_dynamic_indicator(
            indicator_name=self.indicator_name, infile=infile
        )

        # check if result dict contains the right keys
        self.assertListEqual(list(result._fields), ["label", "value", "text", "svg"])


if __name__ == "__main__":
    unittest.main()
