import asyncio
import unittest
from unittest import mock

from ohsome_quality_analyst.base.indicator import Result
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.minimal.indicator import Minimal


class TestBaseIndicator(unittest.TestCase):
    def setUp(self):
        self.feature = asyncio.run(
            db_client.get_feature_from_db(dataset="regions", feature_id="3")
        )
        self.layer_key = "minimal"

    def test_as_feature(self):
        indicator = Minimal(feature=self.feature, layer=mock.Mock())
        feature = indicator.as_feature()
        assert feature.is_valid
        assert feature.geometry == feature.geometry
        for prop in ("result", "metadata", "layer"):
            assert prop in feature["properties"]
        assert "data" not in feature["properties"]

    def test_as_feature_include_data(self):
        indicator = Minimal(feature=self.feature, layer=mock.Mock())
        feature = indicator.as_feature(include_data=True)
        assert feature.is_valid
        for key in ("result", "metadata", "layer", "data"):
            assert key in feature["properties"]
        assert "count" in feature["properties"]["data"]

    def test_as_feature_flatten(self):
        indicator = Minimal(feature=self.feature, layer=mock.Mock())
        feature = indicator.as_feature(flatten=True)
        assert feature.is_valid
        for key in (
            "result.value",
            "metadata.name",
            "layer.name",
        ):
            assert key in feature["properties"]

    def test_data_property(self):
        indicator = Minimal(feature=self.feature, layer=mock.Mock())
        self.assertIsNotNone(indicator.data)
        for key in indicator.data.keys():
            self.assertNotIn(key, ("result", "metadata", "layer", "feature"))

    def test_attribution_class_property(self):
        self.assertIsNotNone(Minimal.attribution())
        self.assertIsInstance(Minimal.attribution(), str)


class TestBaseResult(unittest.TestCase):
    def test_label(self):
        result = Result("", "", "")
        assert result.label == "undefined"
        result.class_ = 4
        assert result.label == "green"
