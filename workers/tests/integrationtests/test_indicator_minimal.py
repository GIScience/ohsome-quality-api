import asyncio
import unittest

from ohsome_quality_analyst.indicators.minimal.indicator import Minimal

from .utils import get_geojson_fixture, get_layer_fixture, oqt_vcr


class TestIndicatorMinimal(unittest.TestCase):
    def setUp(self):
        feature = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        layer = get_layer_fixture("minimal")
        self.indicator = Minimal(feature=feature, layer=layer)

    @oqt_vcr.use_cassette()
    def test(self):
        assert self.indicator.attribution() is not None

        asyncio.run(self.indicator.preprocess())
        assert self.indicator.count is not None

        self.indicator.calculate()
        assert self.indicator.result.label is not None
        assert self.indicator.result.value is not None
        assert self.indicator.result.description is not None
        assert self.indicator.result.timestamp_oqt is not None
        assert self.indicator.result.timestamp_osm is not None

        self.indicator.create_figure()
        assert self.indicator.result.svg is not None


if __name__ == "__main__":
    unittest.main()
