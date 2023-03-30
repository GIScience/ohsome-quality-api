import unittest

import pytest

from ohsome_quality_analyst import definitions
from ohsome_quality_analyst.topics.models import TopicDefinition
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError


class TestDefinitions(unittest.TestCase):
    def test_load_metadata(self):
        metadata = definitions.load_metadata("indicators")
        self.assertIsInstance(metadata, dict)

    def test_get_metadata(self):
        metadata = definitions.get_metadata("indicators", "Minimal")
        self.assertIsInstance(metadata, dict)

    def test_get_indicator_names(self):
        names = definitions.get_indicator_names()
        self.assertIsInstance(names, list)

    def test_get_report_names(self):
        names = definitions.get_report_names()
        self.assertIsInstance(names, list)

    def test_get_topic_keys(self):
        names = definitions.get_topic_keys()
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
                "Global Human Settlement Topic Data; "
                "Earth Observation Group Nighttime Light Data"
            ),
        )

        self.assertRaises(AssertionError, definitions.get_attribution, ["MSO"])

    def test_get_valid_indicators(self):
        indicators = definitions.get_valid_indicators("building_count")
        self.assertEqual(
            indicators,
            (
                "mapping-saturation",
                "currentness",
                "attribute-completeness",
            ),
        )

    def test_get_valid_topics(self):
        topics = definitions.get_valid_topics("minimal")
        self.assertEqual(topics, ("minimal",))

    # This test (and the used variable) is only necessary until the
    # topic-indicator transition is done
    def test_all_valid_indicator_topic_combinations(self):
        # check first direction
        for indicator in definitions.get_indicator_names():
            for topic in definitions.get_valid_topics(indicator):
                assert (indicator, topic) in EXPECTED_INDICATOR_TOPIC
        # check other direction
        for indicator, topic in EXPECTED_INDICATOR_TOPIC:
            assert topic in definitions.get_valid_topics(indicator)
            assert indicator in definitions.get_valid_indicators(topic)


def test_load_topic_definitions():
    topics = definitions.load_topic_definitions()
    for topic in topics:
        assert isinstance(topics[topic], TopicDefinition)


def test_get_topic_definitions():
    topic = definitions.get_topic_definition("minimal")
    assert isinstance(topic, TopicDefinition)


def test_get_topic_definitions_not_found_error():
    with pytest.raises(KeyError):
        definitions.get_topic_definition("foo")
    with pytest.raises(KeyError):
        definitions.get_topic_definition(None)


# Description: constant copy of old definitions.INDICATOR_TOPIC
# to be removed after temporary test_all_valid_indicator_topic_combinations
# becomes unnecessary
EXPECTED_INDICATOR_TOPIC = (
    ("building-completeness", "building_area"),
    ("mapping-saturation", "building_count"),
    ("mapping-saturation", "major_roads_length"),
    ("mapping-saturation", "amenities"),
    ("mapping-saturation", "mapaction_settlements_count"),
    ("mapping-saturation", "mapaction_major_roads_length"),
    ("mapping-saturation", "mapaction_rail_length"),
    ("mapping-saturation", "mapaction_lakes_area"),
    ("mapping-saturation", "mapaction_rivers_length"),
    ("mapping-saturation", "infrastructure_lines"),
    ("mapping-saturation", "poi"),
    ("mapping-saturation", "lulc"),
    ("mapping-saturation", "schools"),
    ("mapping-saturation", "kindergarten"),
    ("mapping-saturation", "clinics"),
    ("mapping-saturation", "doctors"),
    ("mapping-saturation", "bus_stops"),
    ("mapping-saturation", "tram_stops"),
    ("mapping-saturation", "subway_stations"),
    ("mapping-saturation", "supermarkets"),
    ("mapping-saturation", "marketplaces"),
    ("mapping-saturation", "parks"),
    ("mapping-saturation", "forests"),
    ("mapping-saturation", "fitness_centres"),
    ("mapping-saturation", "fire_stations"),
    ("mapping-saturation", "hospitals"),
    ("mapping-saturation", "local_food_shops"),
    ("mapping-saturation", "fast_food_restaurants"),
    ("mapping-saturation", "restaurants"),
    ("mapping-saturation", "supermarkets"),
    ("mapping-saturation", "convenience_stores"),
    ("mapping-saturation", "pubs_and_biergartens"),
    ("mapping-saturation", "alcohol_and_beverages"),
    ("mapping-saturation", "sweets_and_pasteries"),
    ("mapping-saturation", "railway_length"),
    ("mapping-saturation", "clc_arable_land_area"),
    ("mapping-saturation", "clc_permanent_crops_area"),
    ("mapping-saturation", "clc_pastures_area"),
    ("mapping-saturation", "clc_forest_area"),
    ("mapping-saturation", "clc_leaf_type"),
    ("mapping-saturation", "clc_shrub_area"),
    ("mapping-saturation", "clc_open_spaces_area"),
    ("mapping-saturation", "clc_wetland_area"),
    ("mapping-saturation", "clc_water_area"),
    ("mapping-saturation", "clc_waterway_len"),
    ("currentness", "major_roads_count"),
    ("currentness", "building_count"),
    ("currentness", "amenities"),
    ("currentness", "mapaction_settlements_count"),
    ("currentness", "mapaction_major_roads_length"),
    ("currentness", "mapaction_rail_length"),
    ("currentness", "mapaction_lakes_count"),
    ("currentness", "mapaction_rivers_length"),
    ("currentness", "infrastructure_lines"),
    ("currentness", "poi"),
    ("currentness", "lulc"),
    ("currentness", "schools"),
    ("currentness", "kindergarten"),
    ("currentness", "clinics"),
    ("currentness", "doctors"),
    ("currentness", "bus_stops"),
    ("currentness", "tram_stops"),
    ("currentness", "subway_stations"),
    ("currentness", "supermarkets"),
    ("currentness", "marketplaces"),
    ("currentness", "parks"),
    ("currentness", "forests"),
    ("currentness", "fitness_centres"),
    ("currentness", "fire_stations"),
    ("currentness", "hospitals"),
    ("currentness", "local_food_shops"),
    ("currentness", "fast_food_restaurants"),
    ("currentness", "restaurants"),
    ("currentness", "supermarkets"),
    ("currentness", "convenience_stores"),
    ("currentness", "pubs_and_biergartens"),
    ("currentness", "alcohol_and_beverages"),
    ("currentness", "sweets_and_pasteries"),
    ("currentness", "railway_length"),
    ("currentness", "clc_arable_land_area"),
    ("currentness", "clc_permanent_crops_area"),
    ("currentness", "clc_pastures_area"),
    ("currentness", "clc_forest_area"),
    ("currentness", "clc_leaf_type"),
    ("currentness", "clc_shrub_area"),
    ("currentness", "clc_open_spaces_area"),
    ("currentness", "clc_wetland_area"),
    ("currentness", "clc_water_area"),
    ("currentness", "clc_waterway_len"),
    ("poi-density", "poi"),
    ("attribute-completeness", "building_count"),
    ("attribute-completeness", "major_roads_length"),
    ("attribute-completeness", "clc_leaf_type"),
    ("minimal", "minimal"),
)
