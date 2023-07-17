import unittest

import pytest

import ohsome_quality_analyst.indicators.definitions
import ohsome_quality_analyst.reports.definitions
import ohsome_quality_analyst.topics.definitions
from ohsome_quality_analyst import definitions
from ohsome_quality_analyst.indicators.models import (
    IndicatorMetadata as IndicatorMetadata,
)
from ohsome_quality_analyst.reports.base import ReportMetadata as ReportMetadata
from ohsome_quality_analyst.topics.models import TopicDefinition
from ohsome_quality_analyst.utils.exceptions import RasterDatasetUndefinedError


class TestDefinitions(unittest.TestCase):
    def test_get_indicator_names(self):
        names = ohsome_quality_analyst.indicators.definitions.get_indicator_names()
        self.assertIsInstance(names, list)

    def test_get_report_names(self):
        names = ohsome_quality_analyst.reports.definitions.get_report_names()
        self.assertIsInstance(names, list)

    def test_get_topic_keys(self):
        names = ohsome_quality_analyst.topics.definitions.get_topic_keys()
        self.assertIsInstance(names, list)

    def test_get_dataset_names(self):
        names = definitions.get_dataset_names()
        self.assertIsInstance(names, list)

    def test_get_raster_dataset_names(self):
        names = definitions.get_raster_dataset_names()
        self.assertIsInstance(names, list)
        self.assertTrue(names)

    def test_get_fid_fields(self):
        fields = definitions.get_fid_fields()
        self.assertIsInstance(fields, list)

    def test_get_raster_dataset(self):
        raster = definitions.get_raster_dataset("GHS_BUILT_R2018A")
        self.assertIsInstance(raster, definitions.RasterDataset)

    def test_get_raster_dataset_undefined(self):
        with self.assertRaises(RasterDatasetUndefinedError):
            definitions.get_raster_dataset("foo")

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

    def test_get_valid_indicators(self):
        indicators = ohsome_quality_analyst.indicators.definitions.get_valid_indicators(
            "building-count"
        )
        self.assertEqual(
            indicators,
            (
                "mapping-saturation",
                "currentness",
                "attribute-completeness",
            ),
        )

    def test_get_valid_topics(self):
        topics = ohsome_quality_analyst.topics.definitions.get_valid_topics("minimal")
        self.assertEqual(topics, ("minimal",))


def test_load_topic_definition():
    topics = ohsome_quality_analyst.topics.definitions.load_topic_definitions()
    for topic in topics:
        assert isinstance(topics[topic], TopicDefinition)


def test_get_topic_definition():
    topic = ohsome_quality_analyst.topics.definitions.get_topic_definition("minimal")
    assert isinstance(topic, TopicDefinition)


def test_get_topic_definition_not_found_error():
    with pytest.raises(KeyError):
        ohsome_quality_analyst.topics.definitions.get_topic_definition("foo")
    with pytest.raises(KeyError):
        ohsome_quality_analyst.topics.definitions.get_topic_definition(None)


def test_get_topic_definitions():
    topics = ohsome_quality_analyst.topics.definitions.get_topic_definitions()
    assert isinstance(topics, dict)
    for topic in topics.values():
        assert isinstance(topic, TopicDefinition)


def test_get_indicator_definitions():
    indicators = (
        ohsome_quality_analyst.indicators.definitions.get_indicator_definitions()
    )
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, IndicatorMetadata)


def test_get_indicator_definitions_with_project():
    indicators = (
        ohsome_quality_analyst.indicators.definitions.get_indicator_definitions("core")
    )
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, IndicatorMetadata)
        assert indicator.projects == ["core"]


def test_get_report_definitions():
    reports = ohsome_quality_analyst.reports.definitions.get_report_definitions()
    assert isinstance(reports, dict)
    for report in reports.values():
        assert isinstance(report, ReportMetadata)


def test_get_report_definitions_with_project():
    reports = ohsome_quality_analyst.reports.definitions.get_report_definitions("core")
    assert isinstance(reports, dict)
    for report in reports.values():
        assert isinstance(report, ReportMetadata)
        assert report.project == "core"


def test_get_topic_definitions_with_project():
    topics = ohsome_quality_analyst.topics.definitions.get_topic_definitions("core")
    assert isinstance(topics, dict)
    for topic in topics.values():
        assert isinstance(topic, TopicDefinition)
        assert topic.project == "core"


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
