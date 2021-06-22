import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.tags_ratio.indicator import TagsRatio

from .utils import oqt_vcr


class TestIndicatorRatio(unittest.TestCase):
    def setUp(self):
        # Heidelberg
        self.bpolys = asyncio.run(
            db_client.get_bpolys_from_db(
                dataset="regions", feature_id=3, fid_field="ogc_fid"
            )
        )

    @oqt_vcr.use_cassette()
    def test(self):
        indicator = TagsRatio(
            bpolys=self.bpolys,
            layer_name="jrc_health_count",
        )
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_all_features_match(self):
        """Ratio should be 1.0 when all features match expected tags"""
        # TODO: Choose smaller region
        indicator = TagsRatio(layer_name="jrc_health_count", bpolys=self.bpolys)
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, indicator.count_match)
        self.assertEqual(indicator.ratio, 1.0)

        indicator.calculate()

    @oqt_vcr.use_cassette()
    def test_no_features(self):
        """Test area with no features"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            bpolys = geojson.load(f)

        indicator = TagsRatio(layer_name="jrc_health_count", bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.count_all, 0)

        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)

    @oqt_vcr.use_cassette()
    def test_no_filter2(self):
        """Layer with no filter2 for ratio endpoint"""
        with self.assertRaises(ValueError):
            TagsRatio(layer_name="major_roads_length", bpolys=self.bpolys)


if __name__ == "__main__":
    unittest.main()
