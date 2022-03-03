import asyncio
import os
import unittest
from datetime import datetime

import geojson

from ohsome_quality_analyst.indicators.poi_density.indicator import PoiDensity

from .utils import get_layer_fixture, oqt_vcr


class TestIndicatorPoiDensity(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)
        self.indicator = PoiDensity(feature=feature, layer=get_layer_fixture("poi"))

    @oqt_vcr.use_cassette()
    def test(self):
        self.assertIsNotNone(self.indicator.attribution())

        asyncio.run(self.indicator.preprocess())
        self.assertIsNotNone(self.indicator.area_sqkm)
        self.assertIsNotNone(self.indicator.count)
        self.assertIsNotNone(self.indicator.density)
        self.assertIsInstance(self.indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(self.indicator.result.timestamp_oqt, datetime)

        self.indicator.calculate()
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)

        self.indicator.create_figure()
        self.assertIsNotNone(self.indicator.result.svg)


if __name__ == "__main__":
    unittest.main()
