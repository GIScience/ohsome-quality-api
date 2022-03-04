import os
import tempfile
import unittest
from unittest import mock

from ohsome_quality_analyst.utils import definitions
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError


class TestDefinitions(unittest.TestCase):
    def test_load_logging_config(self):
        config = definitions.load_logging_config()
        self.assertIsInstance(config, dict)

    def test_load_metadata(self):
        metadata = definitions.load_metadata("indicators")
        self.assertIsInstance(metadata, dict)

    def test_get_metadata(self):
        metadata = definitions.get_metadata("indicators", "GhsPopComparisonBuildings")
        self.assertIsInstance(metadata, dict)

    def test_load_layer_definitions(self):
        layer_definitions = definitions.load_layer_definitions()
        self.assertIsInstance(layer_definitions, dict)

    def test_get_layer_definitions(self):
        layer_definitions = definitions.get_layer_definition("building_count")
        self.assertIsInstance(layer_definitions, dict)

    def test_get_indicator_names(self):
        names = definitions.get_indicator_names()
        self.assertIsInstance(names, list)

    def test_get_report_names(self):
        names = definitions.get_report_names()
        self.assertIsInstance(names, list)

    def test_get_layer_names(self):
        names = definitions.get_layer_names()
        self.assertIsInstance(names, list)

    def test_get_dataset_names(self):
        names = definitions.get_dataset_names()
        self.assertIsInstance(names, list)

    def test_get_raster_dataset_names(self):
        names = definitions.get_raster_dataset_names()
        self.assertIsInstance(names, list)
        self.assertTrue(names)

    def test_get_fid_fields(self):
        fields = definitions.get_fid_fields()
        self.assertIsInstance(fields, list)

    def test_get_dataset_names_api(self):
        names = definitions.get_dataset_names_api()
        self.assertIsInstance(names, list)
        self.assertIn("regions", names)
        self.assertNotIn("gadm", names)

    def test_get_fid_fields_api(self):
        fields = definitions.get_fid_fields_api()
        self.assertIsInstance(fields, list)
        self.assertIn("name", fields)
        self.assertIn("ogc_fid", fields)

    def test_get_raster_dataset(self):
        raster = definitions.get_raster_dataset("GHS_BUILT_R2018A")
        self.assertIsInstance(raster, definitions.RasterDataset)

    def test_get_raster_dataset_undefined(self):
        with self.assertRaises(RasterDatasetUndefinedError):
            definitions.get_raster_dataset("foo")

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_data_dir_unset_env(self):
        data_dir = definitions.get_data_dir()
        expected = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__),
            ),
            "..",
            "..",
            "..",
            "data",
        )
        self.assertTrue(os.path.samefile(data_dir, expected))

    def test_get_data_dir_set_env(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            custom_data_dir = os.path.join(tmpdirname, "oqt-custom")
            os.mkdir(custom_data_dir)
            with mock.patch.dict(
                "os.environ",
                {"OQT_DATA_DIR": custom_data_dir},
                clear=True,
            ):
                data_dir = definitions.get_data_dir()
            self.assertEqual(data_dir, custom_data_dir)

    @mock.patch.dict(
        "os.environ",
        {"OQT_DATA_DIR": os.path.join(tempfile.gettempdir(), "oqt-foo")},
        clear=True,
    )
    def test_get_data_dir_error(self):
        with self.assertRaises(FileNotFoundError):
            definitions.get_data_dir()

    def test_get_attribution(self):
        attribution = definitions.get_attribution(["OSM"])
        self.assertEqual(attribution, "© OpenStreetMap contributors")

        attributions = definitions.get_attribution(["OSM", "GHSL", "VNL"])
        self.assertEqual(
            attributions,
            (
                "© OpenStreetMap contributors; © European Union, 1995-2022, "
                "Global Human Settlement Layer Data; "
                "Earth Observation Group Nighttime Light Data"
            ),
        )

        self.assertRaises(AssertionError, definitions.get_attribution, ["MSO"])
