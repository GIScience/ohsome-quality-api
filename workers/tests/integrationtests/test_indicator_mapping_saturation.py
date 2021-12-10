import asyncio
import unittest
from datetime import datetime

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
        indicator.calculate()
        self.assertIsInstance(indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(indicator.result.timestamp_oqt, datetime)
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)


if __name__ == "__main__":
    unittest.main()
