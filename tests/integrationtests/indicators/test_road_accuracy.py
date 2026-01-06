import pytest

from ohsome_quality_api.indicators.road_accuracy.indicator import RoadAccuracy


@pytest.mark.asyncio
async def test_preprocess_multi_class(topic_major_roads_length, feature_malta):
    indicator = RoadAccuracy(feature=feature_malta, topic=topic_major_roads_length)
    assert indicator.topic == topic_major_roads_length
