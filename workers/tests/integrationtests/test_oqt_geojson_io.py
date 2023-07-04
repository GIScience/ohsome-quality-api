import asyncio
import unittest

from geojson import FeatureCollection

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import IndicatorBpolys
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import oqt_vcr


class TestOqtGeoJsonIO(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.name = "minimal"
        self.topic_key = "minimal"
        self.dataset = "regions"
        self.feature_id = "3"
        self.feature = asyncio.run(
            db_client.get_feature_from_db(self.dataset, feature_id=self.feature_id)
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_bpolys(self):
        patameters = IndicatorBpolys(
            topic=self.topic_key,
            bpolys=self.feature,
        )
        feature = asyncio.run(
            oqt.create_indicator_as_geojson(patameters, key=self.name)
        )
        self.assertIsInstance(feature, FeatureCollection)

    @oqt_vcr.use_cassette()
    def test_create_indicator_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            asyncio.run(oqt.create_indicator_as_geojson(""))


if __name__ == "__main__":
    unittest.main()
