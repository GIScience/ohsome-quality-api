import asyncio
import os
from datetime import datetime

import geojson
import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)
from tests.integrationtests.utils import get_topic_fixture, oqapi_vcr


class TestPreprocess:
    @oqapi_vcr.use_cassette
    def test_preprocess(
        self, topic_building_count, feature_germany_heidelberg, attribute_key
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette
    def test_preprocess_multiple_attribute_keys(
        self, topic_building_count, feature_germany_heidelberg, attribute_key_multiple
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key_multiple,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_key,
    ):
        i = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key,
        )
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.result.value is not None
        assert indicator.result.value >= 0.0
        assert indicator.result.label != "red"
        assert indicator.result.description is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette()
    def test_no_features(self, attribute):
        """Test area with no features"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = AttributeCompleteness(
            topic=get_topic_fixture("clc-leaf-type"),
            feature=feature,
            attribute_key=["leaf-type"],
        )
        asyncio.run(indicator.preprocess())
        assert indicator.absolute_value_1 == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None


class TestFigure:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_key,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_key,
        )
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        assert indicator.description == (
            '39.51% of all "building count" features (all: 30237 elements) in your '
            "area of interest have the selected additional attribute height of "
            "buildings (matched: 11948 elements)."
        )
        return indicator

    # comment out for manual test
    @pytest.mark.skip(reason="Only for manual testing.")
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure


def test_create_description():
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        "foo",
        ["height"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    assert indicator.description == (
        '20.0% of all "building count" features (all: 10 elements) in your area of '
        "interest have the selected additional attribute height of buildings "
        "(matched: 2 elements)."
    )


def test_create_description_multiple_attributes():
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        "foo",
        ["height", "house-number", "address-street"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    assert indicator.description == (
        '20.0% of all "building count" features (all: 10 elements) in your area of '
        "interest have the selected additional attributes height of buildings, house "
        "number, street address (matched: 2 elements)."
    )


@pytest.mark.parametrize(
    "topic_key, attribute_key, aggregation, "
    "result_value, absolute_value_1, absolute_value_2",
    [
        ("building-count", "height", "elements", 0.2, 10, 2),
        ("clc-leaf-type", "leaf-type", "m²", 0.2, 10.012, 2.012),
        ("roads", "name", "m", 0.2, 10.012, 2.012),
    ],
)
def test_create_description_multiple_aggregation_types(
    topic_key,
    attribute_key,
    aggregation,
    result_value,
    absolute_value_1,
    absolute_value_2,
):
    indicator = AttributeCompleteness(
        get_topic_fixture(topic_key),
        "foo",
        [attribute_key],
    )
    indicator.result.value = result_value
    indicator.absolute_value_1 = absolute_value_1
    indicator.absolute_value_2 = absolute_value_2
    indicator.create_description()
    assert aggregation in indicator.description
