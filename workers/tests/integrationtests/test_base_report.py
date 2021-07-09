import asyncio
import unittest

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)
from ohsome_quality_analyst.reports.simple_report.report import SimpleReport


class TestBaseReport(unittest.TestCase):
    def test_as_feature(self):
        feature = asyncio.run(
            db_client.get_feature_from_db(
                dataset="regions", feature_id="3", fid_field="ogc_fid"
            )
        )
        indicator = GhsPopComparisonBuildings(
            feature=feature, layer_name="building_count"
        )
        report = SimpleReport(feature=feature)
        report.set_indicator_layer()
        for _ in report.indicator_layer:
            report.indicators.append(indicator)

        feature = report.as_feature()
        self.assertTrue(feature.is_valid)

        for i in (
            "0.data.pop_count",
            "0.data.area",
            "0.data.pop_count_per_sqkm",
            "0.data.feature_count",
            "0.data.feature_count_per_sqkm",
        ):
            self.assertIn(i, feature["properties"].keys())
