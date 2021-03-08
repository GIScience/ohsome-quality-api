import asyncio
import unittest

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison.indicator import (
    GhsPopComparison,
)


class TestGeodatabase(unittest.TestCase):
    # TODO: split tests by functionality (load and safe), but load test needs a saved
    # indicator
    def test_save_and_load(self):
        # save
        self.indicator = GhsPopComparison(
            dataset="test_regions", feature_id=2, layer_name="building_count"
        )
        asyncio.run(self.indicator.preprocess())
        self.indicator.calculate()
        self.indicator.create_figure()
        db_client.save_indicator_results(self.indicator)

        # load
        self.indicator = GhsPopComparison(
            dataset="test_regions", feature_id=2, layer_name="building_count"
        )
        db_client.load_indicator_results(self.indicator)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)


if __name__ == "__main__":
    unittest.main()
