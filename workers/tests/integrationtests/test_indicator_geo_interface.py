import asyncio
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.utils.helper import datetime_to_isostring_timestamp

from .utils import oqt_vcr


class TestIndicatorGhsPopComparisonBuildings(unittest.TestCase):
    @oqt_vcr.use_cassette()
    def test(self):
        bpolys = asyncio.run(
            db_client.get_bpolys_from_db(
                dataset="regions", feature_id=31, fid_field="ogc_fid"
            )
        )
        self.indicator = GhsPopComparisonBuildings(
            bpolys=bpolys, layer_name="building_count"
        )

        asyncio.run(self.indicator.preprocess())
        self.indicator.calculate()

        feature = geojson.dumps(self.indicator, default=datetime_to_isostring_timestamp)
        print(feature)
        self.assertTrue(geojson.loads(feature).is_valid)


if __name__ == "__main__":
    unittest.main()
