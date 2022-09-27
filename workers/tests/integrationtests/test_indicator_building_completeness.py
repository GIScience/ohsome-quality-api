import asyncio
import os
import unittest
from datetime import datetime
from unittest import mock

from geojson import FeatureCollection

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.building_completeness.indicator import (
    BuildingCompleteness,
    get_hex_cells,
    get_shdi,
    get_smod_class_share,
)
from ohsome_quality_analyst.utils.exceptions import HexCellsNotFoundError

from .utils import get_layer_fixture, oqt_vcr


class TestIndicatorBuildingCompleteness(unittest.TestCase):
    def setUp(self):
        self.feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="12")
        )
        self.layer = get_layer_fixture("building_area")
        self.indicator = BuildingCompleteness(
            feature=self.feature, layer=self.layer, thresholds=None
        )

    @mock.patch("ohsome_quality_analyst.raster.client.get_config_value")
    @oqt_vcr.use_cassette()
    def test_indicator(self, mock_get_data_dir):
        mock_get_data_dir.return_value = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "raster"
        )
        asyncio.run(self.indicator.preprocess())
        # Data
        self.assertIsInstance(self.indicator.building_area_osm, list)
        self.assertEqual(len(self.indicator.building_area_osm), 9)
        self.assertIsInstance(self.indicator.hex_cell_geohash, list)
        self.assertEqual(len(self.indicator.hex_cell_geohash), 9)
        # Covariates
        self.assertIsInstance(self.indicator.covariates, dict)
        self.assertEqual(len(self.indicator.covariates), 12)
        for key in (
            "urban_centre",
            "dense_urban_cluster",
            "semi_dense_urban_cluster",
            "suburban_or_peri_urban",
            "rural_cluster",
            "low_density_rural",
            "very_low_density_rural",
            "water",
        ):
            self.assertEqual(len(self.indicator.covariates[key]), 9)
            for i in self.indicator.covariates[key]:
                self.assertIsNotNone(i)
                self.assertGreaterEqual(i, 0)
        # Calculate
        self.indicator.calculate()
        self.assertIsInstance(self.indicator.building_area_prediction, list)
        self.assertGreaterEqual(len(self.indicator.building_area_prediction), 0)
        self.assertIsInstance(self.indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(self.indicator.result.timestamp_oqt, datetime)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertLessEqual(self.indicator.result.value, 1.0)
        self.assertGreaterEqual(self.indicator.result.value, 0.0)
        # Create Figure
        self.indicator.create_figure()
        self.assertIsNotNone(self.indicator.result.svg)

    @mock.patch("ohsome_quality_analyst.raster.client.get_config_value")
    def test_get_smod_class_share(self, mock_get_data_dir):
        mock_get_data_dir.return_value = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures", "raster"
        )
        result = get_smod_class_share(FeatureCollection(features=[self.feature]))
        self.assertDictEqual(
            result,
            {
                "urban_centre": [0.05128205128205128],
                "dense_urban_cluster": [0],
                "semi_dense_urban_cluster": [0],
                "suburban_or_peri_urban": [0.029914529914529916],
                "rural_cluster": [0],
                "low_density_rural": [0.017094017094017096],
                "very_low_density_rural": [0.9017094017094017],
                "water": [0],
            },
        )

    def test_get_hex_cells(self):
        result = asyncio.run(get_hex_cells(self.feature))
        self.assertIsInstance(result, FeatureCollection)
        self.assertIsNotNone(result.features)

    def test_get_hex_cells_not_found(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        with self.assertRaises(HexCellsNotFoundError):
            asyncio.run(get_hex_cells(feature))

    def test_get_shdi(self):
        result = asyncio.run(get_shdi(FeatureCollection(features=[self.feature])))
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
