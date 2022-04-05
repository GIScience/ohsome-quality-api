import unittest

import geojson

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst.api.api import (
    empty_api_response,
    remove_svg_from_properties,
)


class TestApi(unittest.TestCase):
    def test_empty_api_response(self):
        response_template = {
            "apiVersion": oqt_version,
            "attribution": {
                "url": (
                    "https://github.com/GIScience/ohsome-quality-analyst/blob/main/"
                    + "data/COPYRIGHTS.md"
                ),
            },
        }
        self.assertDictEqual(response_template, empty_api_response())

    def test_remove_svg_from_properties(self):
        feature = geojson.utils.generate_random("Polygon")
        properties_dict = {"test": "test", "result.svg": "123", "result.label": "green"}
        feature["properties"] = properties_dict
        feature = geojson.Feature(feature)
        feature_1 = geojson.utils.generate_random("Polygon")
        feature_2 = geojson.utils.generate_random("Polygon")
        properties_dict_1 = {"0.result.svg": "123", "result.label": "green"}
        properties_dict_2 = {"1.result.svg": "abc", "result.label": "green"}
        feature_1["properties"] = properties_dict_1
        feature_2["properties"] = properties_dict_2
        feature_collection = geojson.FeatureCollection([feature_1, feature_2])
        remove_svg_from_properties(feature)
        remove_svg_from_properties(feature_collection)
        self.assertNotIn("result.svg", list(feature["properties"].keys()))
        for element in feature_collection["features"]:
            self.assertNotIn("result.svg", list(element["properties"].keys()))

    def test_remove_html_from_properties(self):
        feature = geojson.utils.generate_random("Polygon")
        properties_dict = {
            "test": "test",
            "result.html": "123",
            "result.label": "green",
        }
        feature["properties"] = properties_dict
        feature = geojson.Feature(feature)
        feature_1 = geojson.utils.generate_random("Polygon")
        feature_2 = geojson.utils.generate_random("Polygon")
        properties_dict_1 = {"0.result.html": "123", "result.label": "green"}
        properties_dict_2 = {"1.result.html": "abc", "result.label": "green"}
        feature_1["properties"] = properties_dict_1
        feature_2["properties"] = properties_dict_2
        feature_collection = geojson.FeatureCollection([feature_1, feature_2])
        remove_svg_from_properties(feature)
        remove_svg_from_properties(feature_collection)
        self.assertNotIn("html.svg", list(feature["properties"].keys()))
        for element in feature_collection["features"]:
            self.assertNotIn("html.svg", list(element["properties"].keys()))
