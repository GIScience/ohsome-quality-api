from conftest import feature_land_cover
from ohsome_quality_api.indicators.land_cover_completeness.indicator import LandCoverCompleteness

def test_create_land_cover_completeness(topic_land_cover, feature_land_cover):
    indicator = LandCoverCompleteness(topic=topic_land_cover, feature=feature_land_cover)

