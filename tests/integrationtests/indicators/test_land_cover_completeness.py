import pytest
from approvaltests import verify
from approvaltests_namers import PytestNamer

from ohsome_quality_api.indicators.land_cover_completeness.indicator import (
    LandCoverCompleteness,
)


@pytest.mark.asyncio
async def test_create_land_cover_completeness(topic_land_cover, feature_land_cover):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover, feature=feature_land_cover
    )
    await indicator.preprocess()

    assert indicator.osm_area is not None
    assert indicator.result.timestamp_osm is not None
    verify(indicator.result.description, namer=PytestNamer())


@pytest.mark.asyncio
async def test_create_land_cover_completeness_calculate(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover, feature=feature_land_cover
    )
    await indicator.preprocess()
    indicator.calculate()
    verify(indicator.result.description, namer=PytestNamer())
