import asyncio
from datetime import datetime
from unittest.mock import AsyncMock

import plotly.graph_objects as pgo
import plotly.io as pio
import pytest

from ohsome_quality_api.api.request_models import Feature, FeatureCollection
from ohsome_quality_api.indicators.building_completeness.indicator import (
    BuildingCompleteness,
    get_hex_cells,
    get_shdi,
    get_smod_class_share,
)
from ohsome_quality_api.utils.exceptions import HexCellsNotFoundError
from tests.integrationtests.utils import (
    get_geojson_fixture,
    get_topic_fixture,
    oqapi_vcr,
)


@pytest.fixture(scope="class")
def feature():
    return get_geojson_fixture("algeria-touggourt-feature.geojson")


@pytest.fixture(scope="class")
def topic():
    return get_topic_fixture("building-area")


@pytest.fixture(scope="class")
def hexcells():
    return get_geojson_fixture("algeria-touggourt-hexcells.geojson")


@pytest.fixture(scope="class")
def shdi():
    # fmt: off
    return [0.749352689479516, 0.749352689479516, 0.749352689479516, 0.749352689479516,
            0.749352689479516, 0.749352689479516, 0.749352689479516, 0.749352689479516,
            0.749352689479516]
    # fmt: on


@pytest.fixture(scope="class")
def mock_get_hex_cells(class_mocker, hexcells):
    async_mock = AsyncMock(return_value=hexcells)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_completeness.indicator.get_hex_cells",  # noqa
        side_effect=async_mock,
    )


@pytest.fixture(scope="class")
def mock_get_shdi(class_mocker, shdi):
    async_mock = AsyncMock(return_value=shdi)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_completeness.indicator.get_shdi",
        side_effect=async_mock,
    )


class TestPreprocess:
    @oqapi_vcr.use_cassette
    def test_preprocess(
        self,
        feature,
        topic,
        mock_env_oqapi_data_dir,
        mock_get_hex_cells,
        mock_get_shdi,
    ):
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


class TestCalculationFigure:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(
        self,
        feature,
        topic,
        mock_env_oqapi_data_dir,
        mock_get_hex_cells,
        mock_get_shdi,
    ):
        i = BuildingCompleteness(feature=feature, topic=topic)
        asyncio.run(i.preprocess())
        i.calculate()
        return i

    def test_calculate(self, indicator):
        assert isinstance(indicator.building_area_prediction, list)
        assert len(indicator.building_area_prediction) > 0
        assert isinstance(indicator.result.timestamp_osm, datetime)
        assert isinstance(indicator.result.timestamp, datetime)
        assert indicator.result.label is not None
        assert indicator.result.value is not None
        assert indicator.result.description is not None
        assert indicator.result.value <= 1.0
        assert indicator.result.value >= 0.0

    @pytest.mark.skip(reason="Only for manual testing.")  # comment for manual test
    def test_create_figure_manual(self, indicator):
        indicator.create_figure()
        pio.show(indicator.result.figure)

    def test_create_figure(self, indicator):
        indicator.create_figure()
        assert isinstance(indicator.result.figure, dict)
        pgo.Figure(indicator.result.figure)  # test for valid Plotly figure


class TestGetData:
    def test_get_smod_class_share(self, mock_env_oqapi_data_dir, feature):
        result = get_smod_class_share(
            FeatureCollection[Feature](type="FeatureCollection", features=[feature])
        )
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

    @pytest.mark.skip("dependency on database setup.")
    def test_get_hex_cells(self, feature):
        result = asyncio.run(get_hex_cells(feature))
        assert isinstance(result, FeatureCollection)
        assert result.features is not None

    @pytest.mark.skip("dependency on database setup.")
    def test_get_hex_cells_not_found(self, feature_germany_heidelberg):
        with pytest.raises(HexCellsNotFoundError):
            asyncio.run(get_hex_cells(feature_germany_heidelberg))

    @pytest.mark.skip("dependency on database setup.")
    def test_get_shdi(self, feature):
        result = asyncio.run(
            get_shdi(
                FeatureCollection[Feature](
                    type="FeatureCollection", features=[feature]
                ),
            )
        )
        assert isinstance(result, list)
        assert len(result) == 1
