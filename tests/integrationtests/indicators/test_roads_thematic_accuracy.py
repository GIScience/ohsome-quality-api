import json
from dataclasses import asdict

import asyncpg_recorder
import geojson
import plotly.io as pio
import pytest
from pytest_approval import verify, verify_image, verify_json

from ohsome_quality_api.indicators.roads_thematic_accuracy.indicator import (
    RoadsThematicAccuracy,
)


@pytest.fixture
def feature():
    return geojson.Feature(
        **{
            "type": "Feature",
            "properties": {},
            "geometry": {
                "coordinates": [
                    [
                        [6.965326376011092, 49.255222737173],
                        [6.965326376011092, 49.22127641767389],
                        [7.019481207402663, 49.22127641767389],
                        [7.019481207402663, 49.255222737173],
                        [6.965326376011092, 49.255222737173],
                    ]
                ],
                "type": "Polygon",
            },
        }
    )


@asyncpg_recorder.use_cassette
@pytest.mark.parametrize(
    "attribute",
    (
        "surface",
        "oneway",
        "lanes",
        "name",
        "width",
        None,
    ),
)
@pytest.mark.asyncio
async def test_preprocess(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )
    assert indicator.attribute == attribute
    await indicator.preprocess()
    assert indicator.matched_data is not None
    verify_json(asdict(indicator.matched_data))


@asyncpg_recorder.use_cassette
@pytest.mark.parametrize(
    "attribute",
    (
        "surface",
        "oneway",
        "lanes",
        "name",
        "width",
        None,
    ),
)
@pytest.mark.asyncio
async def test_calculate(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    # non-quality indicator does not have result value
    assert indicator.result.value is None
    verify(indicator.result.description)


@asyncpg_recorder.use_cassette
@pytest.mark.parametrize(
    "attribute",
    (
        "surface",
        "oneway",
        "lanes",
        "name",
        "width",
        None,
    ),
)
@pytest.mark.asyncio
async def test_create_figure(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    fig = pio.from_json(json.dumps(indicator.result.figure))
    verify_image(fig.to_image(format="png"), extension=".png")


@pytest.mark.asyncio
@pytest.mark.skip()
async def test_coverage(feature, topic_roads, attribute):
    indicator = RoadsThematicAccuracy(
        feature=feature,
        topic=topic_roads,
        attribute=attribute,
    )

    result = await indicator.coverage()
    assert result[0].is_valid

    result = await indicator.coverage(inverse=True)
    assert result[0].is_valid
