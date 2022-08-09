import asyncio
import unittest

import geojson

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.indicators.minimal.indicator import Minimal

from .utils import get_geojson_fixture, get_layer_fixture, oqt_vcr


class TestGeodatabase(unittest.TestCase):
    def setUp(self):
        self.dataset = "regions"
        self.feature_id = "3"  # Heidelberg
        self.feature = asyncio.run(
            db_client.get_feature_from_db(self.dataset, self.feature_id)
        )
        self.layer = get_layer_fixture("minimal")

    def test_get_connection(self):
        async def _test_get_connection():
            async with db_client.get_connection() as conn:
                return await conn.fetchrow("SELECT 1")

        result = asyncio.run(_test_get_connection())
        self.assertEqual(result[0], 1)

    @oqt_vcr.use_cassette()
    def test_save_and_load(self):
        # TODO: split tests by functionality (load and safe),
        # but load test needs a saved indicator.
        # save

        async def _fetchval(query):
            async with db_client.get_connection() as conn:
                return await conn.fetchval(query)

        indicator = Minimal(
            layer=self.layer,
            feature=self.feature,
        )
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        asyncio.run(
            db_client.save_indicator_results(indicator, self.dataset, self.feature_id)
        )
        query = (
            "SELECT feature "
            + "FROM results "
            + "WHERE indicator_name = 'Minimal' "
            + "AND layer_key = 'Minimal' "
            + "AND dataset_name = 'regions' "
            + "AND fid = '3';"
        )
        result = asyncio.run(_fetchval(query))
        self.assertTrue(geojson.loads(result).is_valid)

        # load
        indicator = Minimal(layer=self.layer, feature=self.feature)
        result = asyncio.run(
            db_client.load_indicator_results(indicator, self.dataset, self.feature_id)
        )
        self.assertTrue(result)
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)
        self.assertIsNotNone(indicator.result.svg)

        # Test if data attributes were set
        self.assertIsNotNone(indicator.count)

    def test_get_feature_ids(self):
        results = asyncio.run(db_client.get_feature_ids(self.dataset))
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIsInstance(result, str)

        with self.assertRaises(KeyError):
            asyncio.run(db_client.get_feature_ids("foo"))

    def test_get_area_of_bpolys(self):
        result = asyncio.run(db_client.get_area_of_bpolys(self.feature.geometry))
        self.assertIsInstance(result, float)

    # TODO: Add test for dataset which is not regions
    def test_get_feature_from_db(self):
        result = asyncio.run(
            db_client.get_feature_from_db(self.dataset, self.feature_id)
        )
        self.assertTrue(result.is_valid)  # GeoJSON object validation

        with self.assertRaises(ValueError):
            asyncio.run(db_client.get_feature_from_db(self.dataset, "foo"))

    def test_get_regions_as_geojson(self):
        regions = asyncio.run(db_client.get_regions_as_geojson())
        self.assertTrue(regions.is_valid)

    def test_get_regions(self):
        regions = asyncio.run(db_client.get_regions())
        self.assertIsInstance(regions, list)
        for region in regions:
            self.assertIsInstance(region, dict)

    def test_sanity_check_dataset(self):
        self.assertFalse(db_client.sanity_check_dataset("foo"))
        self.assertTrue(db_client.sanity_check_dataset(self.dataset))

    def test_sanity_check_fid_field(self):
        self.assertFalse(db_client.sanity_check_fid_field(self.dataset, "foo"))
        self.assertTrue(db_client.sanity_check_fid_field(self.dataset, "name"))

    def test_type_of(self):
        result = asyncio.run(db_client.type_of(self.dataset, "ogc_fid"))
        self.assertEqual(result, "integer")
        result = asyncio.run(db_client.type_of(self.dataset, "name"))
        self.assertNotEqual(result, "integer")

    def test_map_fid_to_uid(self):
        result = asyncio.run(
            db_client.map_fid_to_uid(self.dataset, self.feature_id, "ogc_fid")
        )
        self.assertEqual(result, "3")

        result = asyncio.run(
            db_client.map_fid_to_uid(self.dataset, "Heidelberg", "name")
        )
        self.assertEqual(result, "3")

    def test_get_shdi_single_intersection_feature(self):
        """Input geometry intersects only with one SHDI region."""
        result = asyncio.run(db_client.get_shdi(self.feature))
        self.assertIsInstance(result[0]["shdi"], float)
        self.assertLessEqual(result[0]["shdi"], 1.0)
        self.assertEqual(len(result), 1)

    def test_get_shdi_single_intersection_featurecollection(self):
        featurecollection = get_geojson_fixture(
            "heidelberg-bahnstadt-bergheim-featurecollection.geojson"
        )
        result = asyncio.run(db_client.get_shdi(featurecollection))
        self.assertIsInstance(result[0]["shdi"], float)
        self.assertLessEqual(result[0]["shdi"], 1.0)
        self.assertIsInstance(result[1]["shdi"], float)
        self.assertLessEqual(result[1]["shdi"], 1.0)
        self.assertEqual(len(result), 2)

    def test_get_shdi_type_error(self):
        with self.assertRaises(TypeError):
            asyncio.run(db_client.get_shdi(self.feature.geometry))

    # Note: This test can only be executed if the whole SHDI is in the database.
    # def test_get_shdi_multiple_intersections(self):
    #     """Input geometry intersects with multiple SHDI-regions."""
    #     geom = geojson.Polygon(
    #         [
    #             [
    #                 [13.610687255859375, 48.671919512374565],
    #                 [14.0350341796875, 48.671919512374565],
    #                 [14.0350341796875, 48.865618158309374],
    #                 [13.610687255859375, 48.865618158309374],
    #                 [13.610687255859375, 48.671919512374565],
    #             ]
    #         ],
    #     )
    #     result = asyncio.run(db_client.get_shdi(geom))
    #     self.assertIsInstance(result[0]["shdi"], float)
    #     self.assertLessEqual(result[0]["shdi"], 1.0)


if __name__ == "__main__":
    unittest.main()
