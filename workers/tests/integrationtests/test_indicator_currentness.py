import asyncio
import os
import unittest
from datetime import datetime

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.currentness.indicator import (
    Currentness,
    get_last_edited_year,
    get_median_year,
)

from .utils import get_topic_fixture, oqt_vcr


class TestIndicatorCurrentness(unittest.TestCase):
    @oqt_vcr.use_cassette()
    def test(self):
        # Heidelberg
        feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )

        indicator = Currentness(
            feature=feature,
            topic=get_topic_fixture("major_roads_count"),
        )
        self.assertIsNotNone(indicator.attribution())

        asyncio.run(indicator.preprocess())
        self.assertIsInstance(indicator.result.timestamp_osm, datetime)
        self.assertIsInstance(indicator.result.timestamp_oqt, datetime)
        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_no_amenities(self):
        """Test area with no amenities"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = Currentness(feature=feature, topic=get_topic_fixture("amenities"))
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.element_count, 0)

        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)

    def test_get_last_edited_year(self):
        given = {"2008": 3, "2009": 0, "2010": 5, "2011": 0}
        expected = 2010
        result = get_last_edited_year(given)
        assert result == expected

    def test_get_last_edited_year_unsorted(self):
        given = {"2008": 3, "2010": 5, "2009": 0, "2011": 0}
        expected = 2010
        result = get_last_edited_year(given)
        assert result == expected

    def test_get_median_year(self):
        given = {"2008": 0.2, "2009": 0, "2010": 0.6, "2011": 0.2}
        expected = 2010
        result = get_median_year(given)
        assert result == expected

        given = {"2008": 0.6, "2009": 0, "2010": 0.2, "2011": 0.2}
        expected = 2008
        result = get_median_year(given)
        assert result == expected


if __name__ == "__main__":
    unittest.main()
