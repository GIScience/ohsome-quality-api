import json

import pytest
from approvaltests import verify

from ohsome_quality_api.indicators.corine_comparison.indicator import CorineComparison
from ohsome_quality_api.topics.models import BaseTopic
from tests.approvaltests_namers import PytestNamer
from tests.conftest import FIXTURE_DIR


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


@pytest.fixture
def mock_db_fetch(monkeypatch):
    async def fetch(*_):
        with open(FIXTURE_DIR / "corine-comparison-db-fetch-results.json", "r") as file:
            return json.load(file)

    monkeypatch.setattr(
        "ohsome_quality_api.indicators.corine_comparison.indicator.client.fetch",
        fetch,
    )


@pytest.mark.asyncio
async def test_preprocess(feature, mock_db_fetch):
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
        indicator.areas,
        indicator.clc_classes_corine,
        indicator.clc_classes_osm,
    ):
        assert isinstance(area, float)
        assert isinstance(clc_class_corine, int)
        assert isinstance(clc_class_corine, int)


@pytest.mark.asyncio
async def test_calculate(feature, mock_db_fetch):
    topic = BaseTopic(key="forest", name="forest", description="forest")
    indicator = CorineComparison(feature=feature, topic=topic)
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.confusion_matrix is not None
    assert indicator.f1_score is not None
    assert indicator.result.value is not None
    assert indicator.result.class_ == 5
    assert indicator.result.label == "green"
    # TODO: make pytestnamer take arguments to make it possible to call
    # verify twice in one test func
    # verify(indicator.result.description, namer=PytestNamer())
    verify(indicator.report, namer=PytestNamer())
