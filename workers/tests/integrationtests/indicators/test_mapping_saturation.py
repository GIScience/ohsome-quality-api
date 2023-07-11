import asyncio
from datetime import datetime

import numpy as np
import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)
from tests.integrationtests.utils import oqt_vcr


class TestCheckEdgeCases:
    @pytest.fixture()
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        return MappingSaturation(topic_building_count, feature_germany_heidelberg)

    def test_no_data(self, indicator):
        indicator.values = [0, 0]
        assert indicator.check_edge_cases() == "No features were mapped in this region."

    def test_not_enough_data(self, indicator):
        indicator.values = [0, 1]
        assert (
            indicator.check_edge_cases()
            == "Not enough data in total available in this region."
        )

    def test_not_enough_data_points(self, indicator):
        indicator.values = [0, 1, 10]
        assert indicator.check_edge_cases() == (
            "Not enough data points available in this regions. "
            + "The Mapping Saturation indicator needs data for at least 36 months."
        )

    def test_data_deleted(self, indicator):
        indicator.values = [i for i in range(36)]
        indicator.values[-1] = 0
        assert (
            indicator.check_edge_cases()
            == "All mapped features in this region have been deleted."
        )

    def test_ok(self, indicator):
        indicator.values = [i for i in range(36)]
        assert indicator.check_edge_cases() == ""


class TestPreprocess:
    @oqt_vcr.use_cassette
    def test_preprocess(self, topic_building_count, feature_germany_heidelberg):
        indicator = MappingSaturation(topic_building_count, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        assert len(indicator.values) > 0
        assert indicator.values[-1] is not None
        assert indicator.values[-1] > 0
        for t in indicator.timestamps:
            assert isinstance(t, datetime)


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = MappingSaturation(topic_building_count, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert indicator.best_fit is not None
        assert len(indicator.fitted_models) > 0

        for fm in indicator.fitted_models:
            assert not np.isnan(np.sum(fm.fitted_values))
            assert np.isfinite(np.sum(fm.fitted_values))

        assert indicator.result.value >= 0.0
        assert indicator.result.label in ["green", "yellow", "red", "undefined"]
        assert indicator.result.description is not None

        assert isinstance(indicator.result.timestamp_osm, datetime)
        assert isinstance(indicator.result.timestamp_oqt, datetime)

    def test_as_feature(self, indicator):
        indicator_feature = indicator.as_feature()
        properties = indicator_feature.properties
        assert properties["result"]["value"] >= 0.0
        assert properties["result"]["label"] in ["green", "yellow", "red", "undefined"]
        assert properties["result"]["description"] is not None
        assert "data" not in properties.keys()

    def test_as_feature_data(self, indicator):
        indicator_feature = indicator.as_feature(include_data=True)
        properties = indicator_feature.properties
        assert properties["data"]["best_fit"]["name"] is not None

        for fm in properties["data"]["fitted_models"]:
            assert not np.isnan(np.sum(fm["fitted_values"]))
            assert np.isfinite(np.sum(fm["fitted_values"]))

    def test_as_feature_flattend(self, indicator):
        indicator_feature = indicator.as_feature(flatten=True, include_data=True)
        properties = indicator_feature.properties
        assert properties["data.best_fit.name"] is not None
        prefix = "data.fitted_models."
        fitted_model_keys = (prefix + "0", prefix + "1", prefix + "2")
        for i, key in enumerate(fitted_model_keys):
            fm = indicator.fitted_models[i]
            for j in range(len(fm.fitted_values)):
                v = properties[f"{key}.fitted_values.{str(j)}"]
                assert not np.isnan(v)
                assert np.isfinite(v)


class TestFigure:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        i = MappingSaturation(topic_building_count, feature_germany_heidelberg)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure
        assert indicator.result.svg is not None


@oqt_vcr.use_cassette
def test_immutable_attribute(
    topic_building_count,
    feature_collection_germany_heidelberg_bahnstadt_bergheim,
):
    """Test changes of attribute values when multiple indicators are created.

    Because of the usage of `np.asarfay()`, which does not copy the input, on an
    object of the rpy2 library the values of those attributes changed when multiple
    objects of the indicator existed. The solution of this problem is to use
    `np.array()` instead.
    """
    indicators = []
    fitted_values = []
    for feature in feature_collection_germany_heidelberg_bahnstadt_bergheim["features"]:
        indicator = MappingSaturation(topic_building_count, feature)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        for fm in indicator.fitted_models:
            fitted_values.append(list(fm.fitted_values))
        indicators.append(indicator)
    fitted_values_2 = []
    for indicator in indicators:
        for fm in indicator.fitted_models:
            fitted_values_2.append(list(fm.fitted_values))
    assert fitted_values == fitted_values_2
