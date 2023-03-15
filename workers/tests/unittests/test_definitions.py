import unittest

from ohsome_quality_analyst import definitions
from ohsome_quality_analyst.base.layer import LayerDefinition
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError


class TestDefinitions(unittest.TestCase):
    def test_load_metadata(self):
        metadata = definitions.load_metadata("indicators")
        self.assertIsInstance(metadata, dict)

    def test_get_metadata(self):
        metadata = definitions.get_metadata("indicators", "Minimal")
        self.assertIsInstance(metadata, dict)

    def test_load_layer_definitions(self):
        layer_definitions = definitions.load_layer_definitions()
        self.assertIsInstance(layer_definitions, dict)

    def test_get_layer_definitions(self):
        layer_definitions = definitions.get_layer_definition("minimal")
        self.assertIsInstance(layer_definitions, LayerDefinition)

    def test_get_indicator_names(self):
        names = definitions.get_indicator_names()
        self.assertIsInstance(names, list)

    def test_get_report_names(self):
        names = definitions.get_report_names()
        self.assertIsInstance(names, list)

    def test_get_layer_keys(self):
        names = definitions.get_layer_keys()
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

    def test_get_raster_dataset(self):
        raster = definitions.get_raster_dataset("GHS_BUILT_R2018A")
        self.assertIsInstance(raster, definitions.RasterDataset)

    def test_get_raster_dataset_undefined(self):
        with self.assertRaises(RasterDatasetUndefinedError):
            definitions.get_raster_dataset("foo")

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

    def test_get_valid_indicators(self):
        indicators = definitions.get_valid_indicators("building_count")
        self.assertEqual(
            indicators,
            (
                "ghs-pop-comparison-buildings",
                "mapping-saturation",
                "currentness",
                "tags-ratio",
            ),
        )

    def test_get_valid_layers(self):
        layers = definitions.get_valid_layers("minimal")
        self.assertEqual(layers, ("minimal",))
