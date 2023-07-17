import asyncio
import os
import unittest

import geojson
from geojson import FeatureCollection

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import IndicatorRequest
from tests.conftest import FIXTURE_DIR

from .utils import oqt_vcr


class TestOqtGeoJsonIO(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.name = "minimal"
        self.topic_key = "minimal"
        path = os.path.join(
            FIXTURE_DIR,
            "feature-collection-germany-heidelberg.geojson",
        )
        with open(path, "r") as f:
            self.feature = geojson.load(f)

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_bpolys(self):
        patameters = IndicatorRequest(
            topic=self.topic_key,
            bpolys=self.feature,
        )
        feature = asyncio.run(
            oqt.create_indicator_as_geojson(patameters, key=self.name)
        )
        self.assertIsInstance(feature, FeatureCollection)


if __name__ == "__main__":
    unittest.main()
