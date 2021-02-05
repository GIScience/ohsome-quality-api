import os
import unittest

import geojson

from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)


class TestIndicatorMappingSaturation(unittest.TestCase):
    def test(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )

        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        layer_name = "major_roads"

        indicator = MappingSaturation(layer_name=layer_name, bpolys=bpolys)
        indicator.preprocess()

        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    def testFloatDivisionByZeroError(self):
        layer_name = "building_count"
        dataset = "test_regions"
        feature_id = 30

        indicator = MappingSaturation(
            layer_name=layer_name, dataset=dataset, feature_id=feature_id
        )
        indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()

    def testCannotConvertNanError(self):
        layer_name = "building_count"
        dataset = "test_regions"
        feature_id = 2

        indicator = MappingSaturation(
            layer_name=layer_name, dataset=dataset, feature_id=feature_id
        )
        indicator.preprocess()
        indicator.calculate()
        indicator.create_figure()


if __name__ == "__main__":
    unittest.main()
