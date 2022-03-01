import asyncio
import unittest

from geojson import Feature

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import IndicatorBpolys, IndicatorDatabase
from ohsome_quality_analyst.geodatabase import client as db_client

from .utils import oqt_vcr


class TestOqtGeoJsonIO(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.name = "GhsPopComparisonBuildings"
        self.layer_name = "building_count"
        self.dataset = "regions"
        self.feature_id = "3"
        self.feature = asyncio.run(
            db_client.get_feature_from_db(self.dataset, feature_id=self.feature_id)
        )

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_bpolys(self):
        patameters = IndicatorBpolys(
            name=self.name,
            layerName=self.layer_name,
            bpolys=self.feature,
        )
        feature = asyncio.run(oqt.create_indicator_as_geojson(patameters))
        self.assertIsInstance(feature, Feature)

    @oqt_vcr.use_cassette()
    def test_create_indicator_as_geojson_database(self):
        parameters = IndicatorDatabase(
            name=self.name,
            layerName=self.layer_name,
            dataset=self.dataset,
            featureId=self.feature_id,
        )
        feature = asyncio.run(oqt.create_indicator_as_geojson(parameters))
        self.assertIsInstance(feature, Feature)


if __name__ == "__main__":
    unittest.main()
