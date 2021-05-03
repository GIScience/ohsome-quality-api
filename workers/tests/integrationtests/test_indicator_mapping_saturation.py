import asyncio
import os
import unittest

import geojson
import vcr

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_BASENAME = os.path.splitext(os.path.basename(__file__))[0]


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
        asyncio.run(indicator.preprocess())

        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def testFloatDivisionByZeroError(self):
        layer_name = "building_count"
        dataset = "test_regions"
        feature_id = 30
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        indicator = MappingSaturation(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def testCannotConvertNanError(self):
        layer_name = "building_count"
        dataset = "test_regions"
        feature_id = 2
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        indicator = MappingSaturation(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()


if __name__ == "__main__":
    unittest.main()
