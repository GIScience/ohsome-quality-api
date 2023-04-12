import unittest

import geojson

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst.api.api import (
    empty_api_response,
    remove_result_item_from_properties,
)


class TestApi(unittest.TestCase):
    def test_empty_api_response(self):
        response_template = {
            "apiVersion": oqt_version,
            "attribution": {
                "url": (
                    "https://github.com/GIScience/ohsome-quality-analyst/blob/main/"
                    + "COPYRIGHTS.md"
                ),
            },
        }
        self.assertDictEqual(response_template, empty_api_response())

    def test_remove_item_from_properties_feature_flatten(self):
        geom = geojson.utils.generate_random("Polygon")
        prop = {"test": "test", "result.svg": "123", "result.label": "green"}
        feature = geojson.Feature(geometry=geom, properties=prop)
        remove_result_item_from_properties(feature, "svg", True)
        self.assertNotIn("result.svg", list(feature["properties"].keys()))
        self.assertIn("result.label", list(feature["properties"].keys()))

    def test_remove_item_from_properties_feature(self):
        geom = geojson.utils.generate_random("Polygon")
        prop = {"test": "test", "result": {"svg": "123", "label": "green"}}
        feature = geojson.Feature(geometry=geom, properties=prop)
        remove_result_item_from_properties(feature, "svg", False)
        self.assertNotIn("svg", list(feature["properties"]["result"].keys()))
        self.assertIn("label", list(feature["properties"]["result"].keys()))

    def test_remove_item_from_properties_feature_collection_flatten(self):
        geom_1 = geojson.utils.generate_random("Polygon")
        geom_2 = geojson.utils.generate_random("Polygon")
        prop_1 = {"0.result.svg": "123", "result.label": "green"}
        prop_2 = {"1.result.svg": "abc", "result.label": "green"}
        feature_1 = geojson.Feature(geometry=geom_1, properties=prop_1)
        feature_2 = geojson.Feature(geometry=geom_2, properties=prop_2)
        feature_collection = geojson.FeatureCollection([feature_1, feature_2])
        remove_result_item_from_properties(feature_collection, "svg", True)
        for element in feature_collection["features"]:
            self.assertNotIn("result.svg", list(element["properties"].keys()))
            self.assertIn("result.label", list(element["properties"].keys()))

    def test_remove_item_from_properties_feature_collection(self):
        geom_1 = geojson.utils.generate_random("Polygon")
        geom_2 = geojson.utils.generate_random("Polygon")
        prop_1 = {"result": {"svg": "123", "label": "green"}}
        prop_2 = {"result": {"svg": "abv", "label": "green"}}
        feature_1 = geojson.Feature(geometry=geom_1, properties=prop_1)
        feature_2 = geojson.Feature(geometry=geom_2, properties=prop_2)
        feature_collection = geojson.FeatureCollection([feature_1, feature_2])
        remove_result_item_from_properties(feature_collection, "svg", False)
        for element in feature_collection["features"]:
            self.assertNotIn("svg", list(element["properties"]["result"].keys()))
            self.assertIn("label", list(element["properties"]["result"].keys()))
