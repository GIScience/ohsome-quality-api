import asyncio
import unittest

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport


class TestBaseReport(unittest.TestCase):
    def test_geo_interface(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id="3", fid_field="ogc_fid"
            )
        )
        indicator = GhsPopComparisonBuildings(
            feature=feature, layer_name="building_count"
        )

        report = SimpleReport()
        report.set_indicator_layer()

        for _ in report.indicator_layer:
            report.indicators.append(indicator)

        feature_collection = report.as_feature_collection()
        self.assertTrue(feature_collection.is_valid)
