import unittest

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison.indicator import (
    GhsPopComparison,
)


class TestGeodatabase(unittest.TestCase):
    def setUp(self):
        self.indicator = GhsPopComparison(
            dataset="test_regions", feature_id=2, layer_name="building_count"
        )

    def test_save(self):
        self.indicator.preprocess()
        self.indicator.calculate()
        self.indicator.create_figure()
        db_client.save_indicator_results(self.indicator)

    def test_load(self):
        db_client.load_indicator_results(self.indicator)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)


if __name__ == "__main__":
    unittest.main()
