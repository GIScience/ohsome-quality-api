import pytest

from ohsome_quality_api.indicators.corine_comparison.indicator import CorineComparison
from ohsome_quality_api.topics.models import BaseTopic


@pytest.fixture
def feature():
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [8.63552791262136, 49.711771844660191],
                    [8.57181432038835, 49.710072815533977],
                    [8.545479368932039, 49.624271844660186],
                    [8.685649271844662, 49.642111650485433],
                    [8.685649271844662, 49.642111650485433],
                    [8.685649271844662, 49.642111650485433],
                    [8.63552791262136, 49.711771844660191],
                ]
            ],
        },
    }


@pytest.mark.asyncio
async def test_preprocess(feature):
    topic = BaseTopic(key="forest", name="forest", description="forest")
    indicator = CorineComparison(feature=feature, topic=topic)
    await indicator.preprocess()
    assert isinstance(indicator.areas, list)
    assert isinstance(indicator.clc_classes_corine, list)
    assert isinstance(indicator.clc_classes_osm, list)
    assert len(indicator.areas) > 0
    assert len(indicator.clc_classes_corine) > 0
    assert len(indicator.clc_classes_osm) > 0
    for area, clc_class_corine, clc_class_corine in zip(
        indicator.areas, indicator.clc_classes_corine, indicator.clc_classes_osm
    ):
        assert isinstance(area, float)
        assert isinstance(clc_class_corine, int)
        assert isinstance(clc_class_corine, int)
