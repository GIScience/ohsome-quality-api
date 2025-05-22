import pytest

from conftest import feature_land_cover
from ohsome_quality_api.indicators.land_cover_completeness.indicator import LandCoverCompleteness

@pytest.mark.asyncio
async def test_create_land_cover_completeness(topic_land_cover, feature_land_cover):
    indicator = LandCoverCompleteness(topic=topic_land_cover, feature=feature_land_cover)
    await indicator.preprocess()

    assert indicator.osm_area is not None
    assert indicator.result.timestamp_osm is not None
