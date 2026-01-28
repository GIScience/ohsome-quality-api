import json
import os
from datetime import datetime
from unittest.mock import patch

import asyncpg_recorder
import geojson
import pytest
import pytest_asyncio
from pydantic_core import to_jsonable_python
from pytest_approval.main import verify, verify_plotly

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.definitions import Color
from ohsome_quality_api.indicators.currentness.indicator import (
    Bin,
    Currentness,
    check_major_edge_cases,
    check_minor_edge_cases,
    create_bin,
    get_median_month,
    get_num_months_last_contrib,
    month_to_year_month,
)
from ohsome_quality_api.topics.definitions import get_topic_preset
from tests.integrationtests.utils import get_topic_fixture, oqapi_vcr


@pytest.fixture(autouse=True, params=[True, False])
def ohsomedb_feature_flag(request, monkeypatch):
    def get_config_value_(key: str):
        if key == "ohsomedb_enabled":
            return request.param
        else:
            return get_config_value(key)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.currentness.indicator.get_config_value",
        get_config_value_,
    )


class TestInit:
    def test_thresholds_default(self, topic_building_count, feature_germany_heidelberg):
        """Test topic specific thresholds setting after init of indicator."""
        indicator = Currentness(topic_building_count, feature_germany_heidelberg)
        assert indicator.up_to_date == 36
        assert indicator.out_of_date == 96
        assert indicator.th_source == ""

    def test_thresholds_topic(self, feature_germany_heidelberg):
        """Test default thresholds setting after init of indicator."""
        indicator = Currentness(
            feature=feature_germany_heidelberg,
            topic=get_topic_fixture("roads"),
        )
        assert indicator.up_to_date == 48
        assert indicator.out_of_date == 96
        assert (
            indicator.th_source
            == "https://wiki.openstreetmap.org/wiki/StreetComplete/Quests"
        )


@pytest.mark.asyncio
class TestPreprocess:
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        indicator = Currentness(topic_building_count, feature_germany_heidelberg)
        await indicator.preprocess()
        assert len(indicator.bin_total.contrib_abs) > 0
        assert indicator.contrib_sum > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)

    @pytest.mark.parametrize(
        "topic_key",
        # three different aggregation types: count, area and length
        ["building-count", "building-area", "roads"],
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_preprocess_aggregation_types(
        self,
        topic_key,
        feature_germany_heidelberg,
    ):
        topic = get_topic_preset(topic_key)
        indicator = Currentness(topic, feature_germany_heidelberg)
        await indicator.preprocess()
        assert len(indicator.bin_total.contrib_abs) > 0
        assert indicator.contrib_sum > 0
        assert isinstance(indicator.result.timestamp, datetime)
        assert isinstance(indicator.result.timestamp_osm, datetime)


@pytest.mark.asyncio
class TestCalculation:
    @pytest_asyncio.fixture
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def indicator(
        self, topic_building_count, feature_germany_heidelberg, request
    ):
        i = Currentness(topic_building_count, feature_germany_heidelberg)
        await i.preprocess()
        return i

    async def test_calculate(self, indicator):
        indicator.calculate()
        assert indicator.result.value >= 0.0
        assert indicator.result.label == "green"
        assert len(indicator.bin_up_to_date.timestamps) == indicator.up_to_date
        assert verify(indicator.result.description)

    async def test_low_contributions(self, indicator):
        indicator.contrib_sum = 20
        indicator.calculate()
        assert verify(indicator.result.description)

    async def test_months_without_edit(self, indicator):
        indicator.contrib_sum = 30
        indicator.bin_total.contrib_abs = [
            0 if i < 13 else c for i, c in enumerate(indicator.bin_total.contrib_abs)
        ]
        indicator.calculate()
        assert verify(indicator.result.description)

    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_no_subway_stations(self):
        """Test area with no subway stations"""
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../fixtures",
            "niger-kanan-bakache.geojson",
        )
        with open(infile, "r") as f:
            feature = geojson.load(f)

        indicator = Currentness(
            feature=feature, topic=get_topic_fixture("subway-stations")
        )
        await indicator.preprocess()
        assert indicator.contrib_sum == 0

        indicator.calculate()
        assert indicator.result.label == "undefined"
        assert indicator.result.value is None
        assert verify(indicator.result.description)
        indicator.create_figure()
        # TODO: test figure
        # assert isinstance(indicator.result.figure, dict)
        # assert verify_plotly(indicator.result.figure)

    @pytest.mark.parametrize(
        "topic_key",
        # three different aggregation types: count, area and length
        ["building-count", "building-area", "roads"],
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_aggregation_types_no_data(
        self,
        topic_key,
        feature_germany_heidelberg,
    ):
        topic = get_topic_preset(topic_key)
        indicator = Currentness(topic, feature_germany_heidelberg)
        await indicator.preprocess()
        if topic_key == "building-count":
            indicator.contrib_sum = 1
        else:
            indicator.contrib_sum = 0.5
        indicator.calculate()
        assert verify(indicator.result.description)

    @pytest.mark.parametrize(
        "topic_key",
        # three different aggregation types: count, area and length
        ["building-count", "building-area", "roads"],
    )
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_calculate_aggregation_types(
        self,
        topic_key,
        feature_germany_heidelberg,
    ):
        topic = get_topic_preset(topic_key)
        indicator = Currentness(topic, feature_germany_heidelberg)
        await indicator.preprocess()
        indicator.calculate()
        assert verify(indicator.result.description)


@pytest.mark.asyncio(scope="class")
class TestFigure:
    @pytest_asyncio.fixture
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = Currentness(topic_building_count, feature_germany_heidelberg)
        await i.preprocess()
        i.calculate()
        i.create_figure()
        return i

    async def test_create_figure(self, indicator):
        assert isinstance(indicator.result.figure, dict)
        assert verify_plotly(indicator.result.figure)

    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_outdated_features_plotting(
        self,
        topic_building_count,
        feature_germany_heidelberg,
    ):
        """Create a figure with features in the out-of-date category only"""
        i = Currentness(topic_building_count, feature_germany_heidelberg)
        await i.preprocess()
        len_contribs = len(i.bin_total.contrib_abs) - 84
        i.bin_total.contrib_abs[:len_contribs] = [0] * len_contribs
        new_total = sum(i.bin_total.contrib_abs)
        i.bin_total.contrib_rel = [
            value / new_total for value in i.bin_total.contrib_abs
        ]
        i.calculate()
        i.create_figure()
        assert verify(json.dumps(to_jsonable_python(i.result.figure)))

    async def test_get_source(self, indicator):
        indicator.th_source = ""
        assert indicator.get_source_text() == ""
        indicator.th_source = "www.foo.org"
        assert (
            indicator.get_source_text() == "<a href='www.foo.org' target='_blank'>*</a>"
        )

    async def test_get_threshold_text(self, indicator):
        assert indicator.get_threshold_text(Color.RED) == "older than 8 years"
        assert (
            indicator.get_threshold_text(Color.YELLOW) == "between 3 years and 8 years"
        )
        assert indicator.get_threshold_text(Color.GREEN) == "younger than 3 years"


@pytest.mark.asyncio
class TestOhsomeAPIOhsomeDBComparison:
    @asyncpg_recorder.use_cassette
    @oqapi_vcr.use_cassette
    async def test_indicator(self, topic_building_count, feature_germany_heidelberg):
        i_api = Currentness(
            topic_building_count,
            feature_germany_heidelberg,
        )
        await i_api.preprocess()
        i_api.calculate()
        i_api.create_figure()

        i_db = Currentness(
            topic_building_count,
            feature_germany_heidelberg,
        )
        await i_db.preprocess()
        i_db.calculate()
        i_db.create_figure()

        assert verify_plotly(i_api.result.figure)
        assert verify_plotly(i_db.result.figure)


def test_get_last_edited_year():
    given = [3, 0, 5, 0]
    expected = 0
    result = get_num_months_last_contrib(given)
    assert result == expected

    given = [0, 0, 5, 0]
    expected = 2
    result = get_num_months_last_contrib(given)
    assert result == expected


def test_get_median_month():
    given = [0.2, 0, 0.6, 0.2]
    expected = 2
    result = get_median_month(given)
    assert result == expected

    given = [0.6, 0, 0.2, 0.2]
    expected = 0
    result = get_median_month(given)
    assert result == expected


def test_month_to_year_month():
    assert month_to_year_month(1) == "1 month"
    assert month_to_year_month(6) == "6 months"
    assert month_to_year_month(12) == "1 year"
    assert month_to_year_month(13) == "1 year 1 month"
    assert month_to_year_month(14) == "1 year 2 months"
    assert month_to_year_month(100) == "8 years 4 months"


def test_create_bin():
    contrib_abs = [10, 20, 30, 40, 50]
    contrib_rel = [0.1, 0.2, 0.3, 0.4, 0.5]
    timestamps = [
        "2023-01-15",
        "2023-02-15",
        "2023-03-15",
        "2023-04-15",
        "2023-05-15",
    ]

    bin_total = Bin(
        contrib_abs,
        contrib_rel,
        timestamps,
    )

    i = 1  # Start index
    j = 4  # End index

    new_bin = create_bin(bin_total, i, j)

    assert new_bin.contrib_abs == [20, 30, 40]
    assert new_bin.contrib_rel == [0.2, 0.3, 0.4]
    assert new_bin.timestamps == ["2023-02-15", "2023-03-15", "2023-04-15"]

    assert (
        len(new_bin.contrib_abs) == len(new_bin.contrib_rel) == len(new_bin.timestamps)
    )


def test_check_major_edge_cases_no_data():
    result = check_major_edge_cases(0)
    assert "no features of the selected topic" in result


def test_check_major_edge_cases_has_data():
    result = check_major_edge_cases(10)
    assert result == ""


def test_check_minor_edge_cases_low_data(bin_total_factory):
    bin_total = bin_total_factory(contrib_abs=10)
    with patch(
        "ohsome_quality_api.indicators.currentness.indicator.get_num_months_last_contrib",
        return_value=0,
    ):
        result = check_minor_edge_cases(10, bin_total, "count")
    assert "less than 25" in result


def test_check_minor_edge_cases_inactivity(bin_total_factory):
    bin_total = bin_total_factory(contrib_abs=100)
    with patch(
        "ohsome_quality_api.indicators.currentness.indicator.get_num_months_last_contrib",
        return_value=12,
    ):
        result = check_minor_edge_cases(100, bin_total, "count")
    assert "no mapping activity for 12 months" in result


def test_check_minor_edge_cases_area_more_than_25(bin_total_factory):
    bin_total = bin_total_factory(contrib_abs=100)
    with patch(
        "ohsome_quality_api.indicators.currentness.indicator.get_num_months_last_contrib",
        return_value=5,
    ):
        result = check_minor_edge_cases(100, bin_total, "area")
    assert result == ""


def test_check_minor_edge_cases_area_less_than_25(bin_total_factory):
    bin_total = bin_total_factory(contrib_abs=10)
    with patch(
        "ohsome_quality_api.indicators.currentness.indicator.get_num_months_last_contrib",
        return_value=5,
    ):
        result = check_minor_edge_cases(10, bin_total, "area")
    assert result == ""
