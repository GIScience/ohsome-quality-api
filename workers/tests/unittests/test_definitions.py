import unittest

from ohsome_quality_analyst.utils import definitions


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

    def test_get_fid_fields(self):
        fields = definitions.get_fid_fields()
        self.assertIsInstance(fields, list)
