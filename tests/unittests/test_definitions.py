import unittest

import pytest

from ohsome_quality_api import definitions
from ohsome_quality_api.indicators.models import (
    IndicatorMetadata as IndicatorMetadata,
)
from ohsome_quality_api.reports.base import ReportMetadata as ReportMetadata


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

        self.assertRaises(AssertionError, definitions.get_attribution, ["MSO"])


def test_load_metadata_indicator():
    metadata = definitions.load_metadata("indicators")
    assert isinstance(metadata, dict)
    for v in metadata.values():
        assert isinstance(v, IndicatorMetadata)


def test_load_metadata_report():
    metadata = definitions.load_metadata("reports")
    assert isinstance(metadata, dict)
    for v in metadata.values():
        assert isinstance(v, ReportMetadata)


def test_load_metadata_wrong_module():
    with pytest.raises(AssertionError):
        definitions.load_metadata("foo")
    with pytest.raises(AssertionError):
        definitions.load_metadata("")


def test_get_metadata_indicator():
    metadata = definitions.get_metadata("indicators", "Minimal")
    assert isinstance(metadata, IndicatorMetadata)


def test_get_metadata_report():
    metadata = definitions.get_metadata("reports", "Minimal")
    assert isinstance(metadata, ReportMetadata)
    with pytest.raises(KeyError):
        definitions.get_metadata("reports", "")


def test_get_metadata_wrong_class():
    with pytest.raises(KeyError):
        definitions.get_metadata("indicators", "foo")
    with pytest.raises(KeyError):
        definitions.get_metadata("indicators", "")
