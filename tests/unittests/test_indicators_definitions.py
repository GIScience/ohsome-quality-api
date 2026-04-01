import asyncio
from unittest.mock import AsyncMock

import geojson
import pytest
from geojson import Feature, Polygon
from pytest_approval.main import verify

from ohsome_quality_api.indicators import definitions, models


@pytest.fixture(scope="class")
def mock_get_reference_coverage(class_mocker):
    async_mock = AsyncMock(
        return_value=Feature(
            geometry=Polygon(
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
    class_mocker.patch(
        "ohsome_quality_api.indicators.building_comparison.indicator.db_client.get_reference_coverage",
        side_effect=async_mock,
    )


def test_get_indicator_keys():
    names = definitions.get_indicator_keys()
    assert isinstance(names, list)


def test_get_valid_indicators():
    indicators = definitions.get_valid_indicators("building-count")
    assert indicators == (
        "mapping-saturation",
        "currentness",
        "attribute-completeness",
        "user-activity",
    )


def test_get_indicator_metadata():
    indicators = definitions.get_indicator_metadata()
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, models.IndicatorMetadata)


def test_get_indicator_metadata_filtered_by_project():
    indicators = definitions.get_indicator_metadata("core")
    assert isinstance(indicators, dict)
    for indicator in indicators.values():
        assert isinstance(indicator, models.IndicatorMetadata)
        assert indicator.projects == ["core"]


def test_get_indicator(metadata_indicator_minimal):
    indicator = definitions.get_indicator("minimal")
    assert indicator == metadata_indicator_minimal["minimal"]


@pytest.mark.usefixtures("locale_de")
def test_get_indicator_de():
    indicator = definitions.get_indicator("mapping-saturation")
    assert verify(indicator.model_dump_json(indent=2))


def test_get_not_existing_indicator():
    with pytest.raises(KeyError):
        definitions.get_indicator("foo")


def test_get_coverage(mock_get_reference_coverage):
    coverage = asyncio.run(
        definitions.get_coverage("building-comparison", inverse=False)
    )
    assert coverage.is_valid
    assert isinstance(coverage, geojson.FeatureCollection)

    coverage = asyncio.run(definitions.get_coverage("building-comparison"))
    assert coverage.is_valid
    assert isinstance(coverage, geojson.FeatureCollection)

    coverage = asyncio.run(
        definitions.get_coverage("building-comparison", inverse=True)
    )
    assert coverage.is_valid
    assert isinstance(coverage, geojson.FeatureCollection)

    coverage = asyncio.run(definitions.get_coverage("mapping-saturation"))
    assert coverage.is_valid
    assert isinstance(coverage, geojson.FeatureCollection)
