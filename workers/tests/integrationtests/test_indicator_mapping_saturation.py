import asyncio
import os
import unittest
from datetime import datetime

import geojson
import numpy as np

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)

from .utils import oqt_vcr


class TestIndicatorMappingSaturation(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )

    @oqt_vcr.use_cassette()
    def test(self):
        indicator = MappingSaturation(
            layer_name="major_roads_length", feature=self.feature
        )
        asyncio.run(indicator.preprocess())
        self.assertIsInstance(indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(indicator.result.timestamp_oqt, datetime)

        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    # TODO: Should an error get raised here?
    @oqt_vcr.use_cassette()
    def test_float_division_by_zero_error(self):
        indicator = MappingSaturation(layer_name="building_count", feature=self.feature)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()

    @oqt_vcr.use_cassette()
    def test_cannot_convert_nan_error(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = MappingSaturation(layer_name="building_count", feature=feature)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()

    @oqt_vcr.use_cassette()
    def test_avoiding_nan_in_sigmoid_curve(self):
        """Test for NaN values of the `saturation` attribute.

        In some areas which contain mapped features, but mapping has happened in very
        few contributions, sometimes not all curves could be calculated correctly and
        those were chosen as the best-fitting curve. As a result, the output contained
        nan-values instead of data or None values. This test checks the fix which avoids
        choosing a curve containing nan values.
        """
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "southsudan-gogrial-west.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = MappingSaturation(layer_name="building_count", feature=feature)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        self.assertFalse(np.isnan(indicator.data["saturation"]))


if __name__ == "__main__":
    unittest.main()
