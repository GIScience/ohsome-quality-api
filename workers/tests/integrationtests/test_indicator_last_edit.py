import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.last_edit.indicator import LastEdit

from .utils import oqt_vcr


class TestIndicatorLastEdit(unittest.TestCase):
    @oqt_vcr.use_cassette()
    def test(self):
        # Heidelberg
        bpolys = asyncio.run(
            db_client.get_bpolys_from_db(
                dataset="regions", feature_id=3, fid_field="ogc_fid"
            )
        )

        indicator = LastEdit(bpolys=bpolys, layer_name="major_roads_count")
        asyncio.run(indicator.preprocess())
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
            bpolys = geojson.load(f)

        indicator = LastEdit(layer_name="amenities", bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        self.assertEqual(indicator.element_count, 0)

        indicator.calculate()
        self.assertEqual(indicator.result.label, "undefined")
        self.assertEqual(indicator.result.value, None)


if __name__ == "__main__":
    unittest.main()
