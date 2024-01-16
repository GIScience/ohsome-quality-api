import asyncio
from unittest.mock import AsyncMock

import geojson
import pytest
from geojson import Polygon

from ohsome_quality_api.indicators import definitions, models


@pytest.fixture(scope="class")
def mock_select_coverage(class_mocker, feature_germany_berlin):
    async def side_effect(*args, **kwargs):
        inverse = args[1]

        if inverse:
            return [
                str(
                    geojson.dumps(
                        Polygon(
                            coordinates=[
                                [
                                    (-180, 90),
                                    (-180, -90),
                                    (180, -90),
                                    (180, 90),
                                    (-180, 90),
                                ]
                            ]
                        )
                    )
                )
            ]
        else:
            return [str(geojson.dumps(Polygon(coordinates=[])))]

    async_mock = AsyncMock(side_effect=side_effect)
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_reference_coverage",
        side_effect=async_mock,
    )


def test_get_indicator_names():
    names = definitions.get_indicator_keys()
    assert isinstance(names, list)


def test_get_valid_indicators():
    indicators = definitions.get_valid_indicators("building-count")
    assert indicators == ("mapping-saturation", "currentness", "attribute-completeness")


def test_get_indicator_definitions():
    indicators = definitions.get_indicator_metadata()
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, models.IndicatorMetadata)


def test_get_indicator_definitions_with_project():
    indicators = definitions.get_indicator_metadata("core")
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, models.IndicatorMetadata)
        assert indicator.projects == ["core"]


def test_get_coverage(mock_select_coverage):
    coverage = asyncio.run(
        definitions.get_coverage("building-comparison", inverse=False)
    )
    assert coverage.is_valid
    coverage_default = asyncio.run(definitions.get_coverage("building-comparison"))
    assert coverage_default.is_valid
    assert coverage == coverage_default
    coverage_inversed = asyncio.run(
        definitions.get_coverage("building-comparison", inverse=True)
    )
    assert coverage_inversed.is_valid
    assert coverage != coverage_inversed
    assert coverage_default != coverage_inversed

    assert isinstance(coverage, geojson.FeatureCollection)
    coverage = asyncio.run(definitions.get_coverage("mapping-saturation"))
    assert coverage.is_valid
    assert isinstance(coverage, geojson.FeatureCollection)
