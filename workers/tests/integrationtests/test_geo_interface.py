import asyncio
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.utils.helper import datetime_to_isostring_timestamp


class TestGeoInterface(unittest.TestCase):
    def test(self):
        feature = asyncio.run(
            db_client.get_region_from_db(feature_id=3, fid_field="ogc_fid")
        )
        indicator = GhsPopComparisonBuildings(
            feature=feature, layer_name="building_count"
        )
        print(indicator.feature)
        print(indicator.__geo_interface__)

        feature = geojson.dumps(indicator, default=datetime_to_isostring_timestamp)
        self.assertTrue(geojson.loads(feature).is_valid)


if __name__ == "__main__":
    unittest.main()
