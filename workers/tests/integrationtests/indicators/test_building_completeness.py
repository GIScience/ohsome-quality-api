import asyncio
from datetime import datetime

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest
from geojson import FeatureCollection

from ohsome_quality_analyst.indicators.building_completeness.indicator import (
    BuildingCompleteness,
    get_hex_cells,
    get_shdi,
    get_smod_class_share,
)
from ohsome_quality_analyst.utils.exceptions import HexCellsNotFoundError
from tests.integrationtests.utils import get_geojson_fixture, get_topic_fixture, oqt_vcr


@pytest.fixture(scope="class")
def feature():
    return get_geojson_fixture("algeria-touggourt-feature.geojson")


@pytest.fixture(scope="class")
def topic():
    return get_topic_fixture("building_area")


class TestPreprocess:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def test_preprocess(self, feature, topic):
        indicator = BuildingCompleteness(topic, feature)
        asyncio.run(indicator.preprocess())
        assert isinstance(indicator.building_area_osm, list)
        assert len(indicator.building_area_osm) == 9
        assert isinstance(indicator.hex_cell_geohash, list)
        assert len(indicator.hex_cell_geohash) == 9
        # Covariates
        assert isinstance(indicator.covariates, dict)
        assert len(indicator.covariates) == 12
        for key in (
            "urban_centre",
            "dense_urban_cluster",
            "semi_dense_urban_cluster",
            "suburban_or_peri_urban",
            "rural_cluster",
            "low_density_rural",
            "very_low_density_rural",
            "water",
        ):
            assert len(indicator.covariates[key]) == 9
            for i in indicator.covariates[key]:
                assert i is not None
                assert i >= 0


class TestCalculation:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, feature, topic):
        i = BuildingCompleteness(feature=feature, topic=topic)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert isinstance(indicator.building_area_prediction, list)
        assert len(indicator.building_area_prediction) > 0
        assert isinstance(indicator.result.timestamp_osm, datetime)
        assert isinstance(indicator.result.timestamp_oqt, datetime)
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.value <= 1.0
        assert indicator.result.value >= 0.0


class TestFigure:
    @pytest.fixture(scope="class")
    @oqt_vcr.use_cassette
    def indicator(self, feature, topic):
        i = BuildingCompleteness(feature=feature, topic=topic)
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


def test_get_smod_class_share(mock_env_oqt_data_dir, feature):
    result = get_smod_class_share(FeatureCollection(features=[feature]))
    assert result == {
        "urban_centre": [0.05128205128205128],
        "dense_urban_cluster": [0],
        "semi_dense_urban_cluster": [0],
        "suburban_or_peri_urban": [0.029914529914529916],
        "rural_cluster": [0],
        "low_density_rural": [0.017094017094017096],
        "very_low_density_rural": [0.9017094017094017],
        "water": [0],
    }


def test_get_hex_cells(feature):
    result = asyncio.run(get_hex_cells(feature))
    assert isinstance(result, FeatureCollection)
    assert result.features is not None


def test_get_hex_cells_not_found(feature):
    feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
    with pytest.raises(HexCellsNotFoundError):
        asyncio.run(get_hex_cells(feature))


def test_get_shdi(feature):
    result = asyncio.run(get_shdi(FeatureCollection(features=[feature])))
    assert isinstance(result, list)
    assert len(result) == 1
