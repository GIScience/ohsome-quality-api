import unittest

import geojson

import ohsome_quality_analyst.api.api as api


class TestRemoveSvgFromProperties(unittest.TestCase):
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
        api.remove_svg_from_properties(feature)
        api.remove_svg_from_properties(feature_collection)
        self.assertNotIn("result.svg", list(feature["properties"].keys()))
        for element in feature_collection["features"]:
            self.assertNotIn("result.svg", list(element["properties"].keys()))
