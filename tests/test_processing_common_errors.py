import os
import unittest
from typing import Dict

from ohsome_quality_tool.utils.definitions import get_indicator_classes

INDICATOR_CLASSES: Dict = get_indicator_classes()


class TestProcessingCommonErrors(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def testMappingSaturationFloatDivisionByZeroError(self):
        """Test float division by zero."""

        self.indicator_name = "mapping-saturation"
        self.layer_name = "building-count"
        self.dataset = "test-regions"
        self.feature_id = 30

        indicator = INDICATOR_CLASSES[self.indicator_name](
            dynamic=False,
            dataset=self.dataset,
            feature_id=self.feature_id,
            layer_name=self.layer_name,
        )
        result = indicator.run_processing()

        # check if result contains the right quality level
        self.assertEqual(result.label, "UNDEFINED")

    def testMappingSaturationCannotConvertNanError(self):
        """Test float division by zero."""

        self.indicator_name = "mapping-saturation"
        self.layer_name = "building-count"
        self.dataset = "test-regions"
        self.feature_id = 30

        indicator = INDICATOR_CLASSES[self.indicator_name](
            dynamic=False,
            dataset=self.dataset,
            feature_id=self.feature_id,
            layer_name=self.layer_name,
        )
        result = indicator.run_processing()

        # check if result contains the right quality level
        self.assertEqual(result.label, "UNDEFINED")


if __name__ == "__main__":
    unittest.main()
