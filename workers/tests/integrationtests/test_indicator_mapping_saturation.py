import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)

from .utils import oqt_vcr


class TestIndicatorMappingSaturation(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id=3, fid_field="ogc_fid"
            )
        )

    @oqt_vcr.use_cassette()
    def test(self):
        indicator = MappingSaturation(
            layer_name="major_roads_length", feature=self.feature
        )
        asyncio.run(indicator.preprocess())

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


if __name__ == "__main__":
    unittest.main()
