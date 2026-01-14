import pytest

from ohsome_quality_api.api.request_models import RoadsThematicAccuracyAttribute
from ohsome_quality_api.indicators.roads_thematic_accuracy.indicator import (
    RoadsThematicAccuracy,
)


@pytest.fixture
def roads_thematic_accuracy_attribute() -> RoadsThematicAccuracyAttribute:
    return RoadsThematicAccuracyAttribute.name


@pytest.mark.asyncio
async def test_preprocess_multi_class(
    topic_major_roads_length, feature_malta, roads_thematic_accuracy_attribute
):
    indicator = RoadsThematicAccuracy(
        feature=feature_malta,
        topic=topic_major_roads_length,
        roads_thematic_accuracy_attribute=roads_thematic_accuracy_attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
