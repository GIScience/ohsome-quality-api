import asyncio
import os
from datetime import datetime

import geojson
import pytest
from approvaltests import Options, verify, verify_as_json
from pydantic_core import to_jsonable_python

from ohsome_quality_api.attributes.definitions import get_attributes
from ohsome_quality_api.indicators.attribute_completeness.indicator import (
    AttributeCompleteness,
)
from tests.approvaltests_namers import PytestNamer
from tests.approvaltests_reporters import PlotlyDiffReporter
from tests.integrationtests.utils import (
    get_topic_fixture,
    oqapi_vcr,
)


class TestPreprocess:
    @oqapi_vcr.use_cassette
    def test_preprocess_attribute_keys_single(
        self, topic_building_count, feature_germany_heidelberg, attribute_key
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_keys=attribute_key,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette
    def test_preprocess_attribute_keys_multiple(
        self, topic_building_count, feature_germany_heidelberg, attribute_key_multiple
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_keys=attribute_key_multiple,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @oqapi_vcr.use_cassette
    def test_preprocess_attribute_filter(
        self,
        topic_building_count,
        feature_germany_heidelberg,
        attribute_filter,
        attribute_title,
    ):
        indicator = AttributeCompleteness(
            topic_building_count,
            feature_germany_heidelberg,
            attribute_filter=attribute_filter,
            attribute_title=attribute_title,
        )
        asyncio.run(indicator.preprocess())
        assert indicator.result.value is not None
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


class TestCalculation:
    @pytest.fixture(
        scope="class",
        params=(
            ["height"],
            {
                "attribute_filter": "height=* or building:levels=*",
                "attribute_title": "Height",
            },
        ),
    )
    @oqapi_vcr.use_cassette
    def indicator(self, request, topic_building_count, feature_germany_heidelberg):
        if isinstance(request.param, list):
            i = AttributeCompleteness(
                topic_building_count,
                feature_germany_heidelberg,
                attribute_keys=request.param,
            )
        else:
            i = AttributeCompleteness(
                topic_building_count,
                feature_germany_heidelberg,
                attribute_filter=request.param["attribute_filter"],
                attribute_title=request.param["attribute_title"],
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
        verify(indicator.result.description, namer=PytestNamer())

    @oqapi_vcr.use_cassette
    def test_no_features(self):
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
            attribute_keys=["leaf-type"],
        )
        asyncio.run(indicator.preprocess())
        assert indicator.absolute_value_1 == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None


class TestFigure:
    @pytest.fixture(
        scope="class",
        params=(
            ["height"],
            {
                "attribute_filter": "height=* or building:levels=*",
                "attribute_title": "Height",
            },
        ),
    )
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        request,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        if isinstance(request.param, list):
            indicator = AttributeCompleteness(
                topic_building_count, feature_germany_heidelberg, request.param
            )
        else:
            indicator = AttributeCompleteness(
                topic_building_count,
                feature_germany_heidelberg,
                attribute_filter=request.param["attribute_filter"],
                attribute_title=request.param["attribute_title"],
            )
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        return indicator

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        verify_as_json(
            to_jsonable_python(indicator.result.figure),
            options=Options()
            .with_reporter(PlotlyDiffReporter())
            .with_namer(PytestNamer()),
        )


def test_create_description_attribute_keys_single():
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        "foo",
        ["height"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    verify(indicator.description, namer=PytestNamer())


def test_create_description_attribute_keys_multiple():
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        "foo",
        ["height", "house-number", "address-street"],
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    verify(indicator.description, namer=PytestNamer())


def test_create_description_attribute_filter(attribute_filter, attribute_title):
    indicator = AttributeCompleteness(
        get_topic_fixture("building-count"),
        "foo",
        attribute_filter=attribute_filter,
        attribute_title=attribute_title,
    )
    indicator.result.value = 0.2
    indicator.absolute_value_1 = 10
    indicator.absolute_value_2 = 2
    indicator.create_description()
    verify(indicator.description, namer=PytestNamer())


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


def test_filters_match(topic_key_building_count, attribute_key_height):
    indicator_attribute_keys = AttributeCompleteness(
        get_topic_fixture(topic_key_building_count),
        "foo",
        attribute_keys=attribute_key_height,
    )

    attributes = get_attributes()
    indicator_attribute_filter = AttributeCompleteness(
        get_topic_fixture(topic_key_building_count),
        "foo",
        attribute_filter=attributes[topic_key_building_count][
            attribute_key_height[0]
        ].filter,
    )

    assert (
        indicator_attribute_filter.attribute_filter
        == indicator_attribute_keys.attribute_filter
    )
