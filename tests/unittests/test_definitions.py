import unittest

from ohsome_quality_api import definitions
from ohsome_quality_api.indicators.models import (
    IndicatorMetadata as IndicatorMetadata,
)


class TestDefinitions(unittest.TestCase):
    def test_get_attribution(self):
        attribution = definitions.get_attribution(["OSM"])
        self.assertEqual(attribution, "© OpenStreetMap contributors")

        attributions = definitions.get_attribution(["OSM", "GHSL", "VNL"])
        self.assertEqual(
            attributions,
            (
                "© OpenStreetMap contributors; © European Union, 1995-2022, "
                "Global Human Settlement Topic Data; "
                "Earth Observation Group Nighttime Light Data"
            ),
        )

        self.assertRaises(ValueError, definitions.get_attribution, ["MSO"])
