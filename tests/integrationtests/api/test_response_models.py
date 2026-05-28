import asyncio

import pytest

from ohsome_quality_api.api.response_models import (
    CompIndicator,
    IndicatorGeoJSONResponse,
    IndicatorJSONResponse,
)
from ohsome_quality_api.indicators.currentness.indicator import Currentness
from tests.integrationtests.utils import oqapi_vcr


class TestIndicatorResponseModels:
    @pytest.fixture(scope="class")
    @oqapi_vcr.use_cassette
    def indicator(self, topic_building_count, feature_germany_heidelberg):
        indicator = Currentness(topic_building_count, feature_germany_heidelberg)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()
        return indicator

    def test_indicator_property(self, indicator):
        raw_dict = indicator.as_dict(exclude_label=True)
        CompIndicator(**raw_dict)

    def test_indicator_json_response(self, indicator):
        raw_dict = indicator.as_dict(exclude_label=True)
        result_dict = {"result": [raw_dict]}
        IndicatorJSONResponse(**result_dict)

    def test_indicator_geojson_response(self, indicator):
        feature = indicator.as_feature(exclude_label=True)
        result_dict = {"type": "FeatureCollection", "features": [feature]}
        IndicatorGeoJSONResponse(**result_dict)
