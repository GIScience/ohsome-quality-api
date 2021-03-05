# import os
import unittest

from ohsome_quality_analyst.indicators.ratio.indicator import Ratio

# import geojson


class TestIndicatorRatio(unittest.TestCase):
    """def test(self):
    infile = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fixtures",
        "heidelberg_altstadt.geojson",
    )
    with open(infile, "r") as f:
        bpolys = geojson.load(f)
    indicator = Ratio(bpolys=bpolys, layer_name="major_roads")
    indicator.preprocess()
    indicator.calculate()
    self.assertIsNotNone(indicator.result.label)
    self.assertIsNotNone(indicator.result.value)
    self.assertIsNotNone(indicator.result.description)

    indicator.create_figure()
    self.assertIsNotNone(indicator.result.svg)"""

    '''def test_more_edited_features_then_features(self):
        """It can happen that edited features includes deleted features"""
        indicator = Ratio(
            layer_name="amenities", dataset="test_regions", feature_id=7
        )
        indicator.preprocess()


    def test_no_amenities(self):
        """Test area with no amenities"""
        indicator = Ratio(
            layer_name="amenities", dataset="test_regions", feature_id=2
        )
        indicator.preprocess()
        self.assertEqual(indicator.total_features, 0)
        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)'''

    def testAllRegions(self):
        layer_name = "jrc_cultural_heritage_site_count_ratio"
        dataset = "test_regions"
        for region in range(0, 38):
            if region != 12:
                feature_id = region
                print("feature_id")
                print(feature_id)
                indicator = Ratio(
                    layer_name=layer_name, dataset=dataset, feature_id=feature_id
                )
                indicator.preprocess()
                indicator.calculate()
                indicator.create_figure(str(feature_id))


if __name__ == "__main__":
    unittest.main()
