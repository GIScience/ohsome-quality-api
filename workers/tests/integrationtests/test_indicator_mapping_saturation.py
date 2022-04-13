import asyncio
import unittest
from datetime import datetime

import numpy as np

from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)

from .utils import get_geojson_fixture, get_layer_fixture, oqt_vcr


class TestIndicatorMappingSaturation(unittest.TestCase):
    def setUp(self):
        self.feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        self.layer = get_layer_fixture("major_roads_length")

    @oqt_vcr.use_cassette()
    def test(self):
        # Heidelberg
        indicator = MappingSaturation(layer=self.layer, feature=self.feature)
        self.assertIsNotNone(indicator.attribution())

        asyncio.run(indicator.preprocess())
        self.assertTrue(indicator.values)  # No empty list
        self.assertIsNotNone(indicator.latest_value)
        self.assertTrue(indicator.timestamps)

        indicator.calculate()
        self.assertIsInstance(indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(indicator.result.timestamp_oqt, datetime)
        self.assertIsNotNone(indicator.best_fit)
        self.assertTrue(indicator.fitted_models)

        self.assertLessEqual(indicator.result.value, 1.0)
        self.assertGreaterEqual(indicator.result.value, 0.0)

        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

        for fm in indicator.fitted_models:
            self.assertFalse(np.isnan(np.sum(fm.fitted_values)))
            self.assertTrue(np.isfinite(np.sum(fm.fitted_values)))

    @oqt_vcr.use_cassette()
    def test_as_feature(self):
        indicator = MappingSaturation(layer=self.layer, feature=self.feature)
        asyncio.run(indicator.preprocess())
        indicator.calculate()

        indicator_feature = indicator.as_feature()
        properties = indicator_feature.properties
        self.assertIsNotNone(properties["data"]["best_fit"]["name"])

        for fm in properties["data"]["fitted_models"]:
            self.assertFalse(np.isnan(np.sum(fm["fitted_values"])))
            self.assertTrue(np.isfinite(np.sum(fm["fitted_values"])))

        indicator_feature = indicator.as_feature(flatten=True)
        properties = indicator_feature.properties
        self.assertIsNotNone(properties["data.best_fit.name"])

        prefix = "data.fitted_models."
        fitted_model_keys = (prefix + "0", prefix + "1", prefix + "2")
        for i, key in enumerate(fitted_model_keys):
            fm = indicator.fitted_models[i]
            for j in range(len(fm.fitted_values)):
                v = properties[f"{key}.fitted_values.{str(j)}"]
                self.assertFalse(np.isnan(v))
                self.assertTrue(np.isfinite(v))

    @oqt_vcr.use_cassette()
    def test_immutable_attribute(self):
        """Test changes of attribute values when multiple indicators are created.

        Because of the usage of `np.asarfay()`, which does not copy the input, on an
        object of the rpy2 library the values of those attributes changed when multiple
        objects of the indicator existed. The solution of this problem is to use
        `np.array()` instead.
        """
        featurecollection = get_geojson_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        indicators = []
        fitted_values = []
        for feature in featurecollection["features"]:
            indicator = MappingSaturation(
                layer=get_layer_fixture("building_count"),
                feature=feature,
            )
            asyncio.run(indicator.preprocess())
            indicator.calculate()
            for fm in indicator.fitted_models:
                fitted_values.append(list(fm.fitted_values))
            indicators.append(indicator)
        fitted_values_2 = []
        for indicator in indicators:
            for fm in indicator.fitted_models:
                fitted_values_2.append(list(fm.fitted_values))
        self.assertListEqual(fitted_values, fitted_values_2)


if __name__ == "__main__":
    unittest.main()
