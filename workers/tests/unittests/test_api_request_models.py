"""Test module for the `pydantic` data models for API requests"""
import itertools
import json
import os
import unittest

import pytest
from pydantic import ValidationError

from ohsome_quality_analyst.api import request_models
from ohsome_quality_analyst.utils.exceptions import (
    GeoJSONError,
    GeoJSONGeometryTypeError,
    GeoJSONObjectTypeError,
)


class TestApiRequestModels(unittest.TestCase):
    def setUp(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as file:
            self.bpolys = json.load(file)

    def test_topic_key_valid(self):
        # Test on BaseIndicator because validation of BaseTopic needs indicator name
        request_models.BaseTopicName(topic="building-count")

    def test_topic_key_invalid(self):
        # Test on BaseIndicator because validation of BaseTopic needs indicator name
        with self.assertRaises(ValueError):
            request_models.BaseTopicName(topic="foo")

    def test_topic_data_valid(self):
        topic = {
            "key": "foo",
            "name": "bar",
            "description": "buz",
            "data": {},
        }
        request_models.BaseTopicData(topic=topic)

    def test_topic_data_invalid(self):
        for topic in (
            {"key": "foo", "name": "bar", "data": {}},
            {"key": "foo", "description": "bar", "data": {}},
            {"key": "foo", "name": "bar", "description": "buz"},
            {"key": "foo", "name": "bar", "description": "buz", "data": "fis"},
        ):
            with self.assertRaises(ValueError):
                request_models.BaseTopicData(topic=topic)

    def test_invalid_set_of_arguments(self):
        param_keys = (
            "topic",
            "dataset",
            "featureId",
            "fidField",
            "bpolys",
        )
        param_values = (
            "minimal",
            "regions",
            "3",
            "ogc_fid",
            "bpolys",
        )
        all_combinations = []
        for i, _ in enumerate(param_keys):
            for key_comb, val_comb in zip(
                itertools.combinations(param_keys, i),
                itertools.combinations(param_values, i),
            ):
                all_combinations.append(
                    {key: value for key, value in zip(key_comb, val_comb)}
                )
        valid_combinations = (
            {
                "topic": "minimal",
                "dataset": "regions",
                "featureId": "3",
            },
            {
                "topic": "minimal",
                "dataset": "regions",
                "featureId": "3",
                "fidField": "ogc_fid",
            },
            {
                "topic": "minimal",
                "bpolys": self.bpolys,
            },
        )
        for combination in all_combinations:
            if combination in valid_combinations:
                continue
            with self.assertRaises(ValueError):
                request_models.IndicatorBpolys(**combination)


def test_base_indicator_valid():
    request_models.BaseIndicator()
    request_models.BaseIndicator(
        include_svg=True,
        include_html=True,
        include_data=True,
        flatten=True,
    )


def test_base_indicator_invalid():
    with pytest.raises(ValueError):
        request_models.BaseIndicator(include_svg="foo")
    with pytest.raises(ValueError):
        request_models.BaseIndicator(include_html="foo")
    with pytest.raises(ValueError):
        request_models.BaseIndicator(include_data="foo")
    with pytest.raises(ValueError):
        request_models.BaseIndicator(flatten="foo")


def test_base_report_valid():
    request_models.BaseReport()
    request_models.BaseReport(
        include_svg=True,
        include_html=True,
        include_data=False,
        flatten=False,
    )


def test_base_report_invalid():
    with pytest.raises(ValueError):
        request_models.BaseReport(include_svg="foo")
    with pytest.raises(ValueError):
        request_models.BaseReport(include_html="foo")
    with pytest.raises(ValueError):
        request_models.BaseReport(include_data="foo")
    with pytest.raises(ValueError):
        request_models.BaseReport(flatten="foo")


def test_bpolys_valid(
    feature_collection_germany_heidelberg,
    feature_collection_germany_heidelberg_bahnstadt_bergheim,
):
    # Single Feature
    request_models.BaseBpolys(bpolys=feature_collection_germany_heidelberg)
    # Multiple Features
    request_models.BaseBpolys(
        bpolys=feature_collection_germany_heidelberg_bahnstadt_bergheim
    )


def test_bpolys_invalid(feature_collection_invalid):
    with pytest.raises((GeoJSONError, ValidationError)):
        request_models.BaseBpolys(bpolys=feature_collection_invalid)


# TODO
@pytest.mark.skip(reason="Support for Feature will be discontinued.")
def test_bpolys_unsupported_object_type_feature(feature_germany_heidelberg):
    with pytest.raises((GeoJSONObjectTypeError, ValidationError)):
        request_models.BaseBpolys(bpolys=feature_germany_heidelberg)


def test_bpolys_unsupported_object_type(geojson_unsupported_object_type):
    with pytest.raises((GeoJSONObjectTypeError, ValidationError)):
        request_models.BaseBpolys(bpolys=geojson_unsupported_object_type)


def test_bpolys_unsupported_geometry_type(feature_collection_unsupported_geometry_type):
    with pytest.raises((GeoJSONGeometryTypeError, ValidationError)):
        request_models.BaseBpolys(bpolys=feature_collection_unsupported_geometry_type)


def test_indicator_bpolys(feature_collection_germany_heidelberg):
    request_models.IndicatorBpolys(
        topic="minimal",
        bpolys=feature_collection_germany_heidelberg,
    )


def test_indicator_data(feature_collection_germany_heidelberg):
    request_models.IndicatorData(
        bpolys=feature_collection_germany_heidelberg,
        topic={"key": "foo", "name": "bar", "description": "buz", "data": {}},
    )
