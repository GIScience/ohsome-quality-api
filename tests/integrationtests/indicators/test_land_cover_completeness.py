import pytest
from approvaltests import verify

from ohsome_quality_api.indicators.land_cover_completeness.indicator import (
    LandCoverCompleteness,
)
from tests.approvaltests_namers import PytestNamer
from tests.integrationtests.utils import oqapi_vcr


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_preprocess(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    verify(indicator.osm_area_ratio, namer=PytestNamer(postfix="osm_area_ratio"))
    verify(indicator.result.timestamp_osm, namer=PytestNamer(postfix="timestamp_osm"))


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_calculate(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    indicator.calculate()
    assert indicator.result.label == "green"
    verify(indicator.osm_area_ratio, namer=PytestNamer(postfix="osm_area_ratio"))
    verify(indicator.result.value, namer=PytestNamer(postfix="value"))
    verify(indicator.result.class_, namer=PytestNamer(postfix="class_"))
    verify(indicator.result.description, namer=PytestNamer(postfix="description"))


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_land_cover_completeness_calculate_above_100(
    topic_land_cover, feature_land_cover
):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover,
        feature=feature_land_cover,
    )
    await indicator.preprocess()
    indicator.osm_area_ratio = 1300000
    indicator.calculate()
    assert indicator.result.label == "green"
    verify(
        indicator.result.description, namer=PytestNamer(postfix="description_above_100")
    )


@pytest.mark.asyncio
@oqapi_vcr.use_cassette
async def test_create_figure(topic_land_cover, feature_land_cover):
    indicator = LandCoverCompleteness(
        topic=topic_land_cover, feature=feature_land_cover
    )
    await indicator.preprocess()
    indicator.calculate()
    indicator.create_figure()
    assert isinstance(indicator.result.figure, dict)


#   verify_as_json(
#       to_jsonable_python(indicator.result.figure),
#       options=Options().with_reporter(PlotlyDiffReporter()).with_namer(PytestNamer()),
#   )
