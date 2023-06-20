import asyncio
import os
import unittest

import geojson
from geojson import Feature, FeatureCollection

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import IndicatorBpolys, IndicatorDatabase

from .utils import oqt_vcr


class TestOqtGeoJsonIO(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.name = "minimal"
        self.topic_key = "minimal"
        self.dataset = "regions"
        self.feature_id = "3"

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_bpolys(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson",
        )
        with open(path, "r") as f:
            feature = geojson.load(f)
        parameters = IndicatorBpolys(
            topic=self.topic_key,
            bpolys=feature,
        )
        feature = asyncio.run(
            oqt.create_indicator_as_geojson(parameters, key=self.name)
        )
        self.assertIsInstance(feature, FeatureCollection)

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_database(self):
        parameters = IndicatorDatabase(
            topic=self.topic_key,
            dataset=self.dataset,
            feature_id=self.feature_id,
        )
        feature = asyncio.run(oqt.create_indicator_as_geojson(parameters, self.name))
        self.assertIsInstance(feature, Feature)

    @oqt_vcr.use_cassette()
    def test_create_indicator_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            asyncio.run(oqt.create_indicator_as_geojson(""))


if __name__ == "__main__":
    unittest.main()
