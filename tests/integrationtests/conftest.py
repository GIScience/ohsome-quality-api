import pytest

from tests.integrationtests.utils import get_geojson_fixture


@pytest.fixture
def europe():
    return get_geojson_fixture("europe.geojson")
