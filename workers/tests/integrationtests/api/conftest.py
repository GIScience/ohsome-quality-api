import pytest
from fastapi.testclient import TestClient

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst.api.api import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def response_template():
    return {
        "api-version": oqt_version,
        "attribution": {
            "url": (
                "https://github.com/GIScience/ohsome-quality-analyst/blob/main/"
                + "COPYRIGHTS.md"
            ),
        },
    }


@pytest.fixture
def metadata_topic_building_count():
    return {
        "name": "Building Count",
        "description": (
            "All buildings as defined by all objects tagged with 'building=*'."
        ),
        "endpoint": "elements/count",
        "filter": "building=* and building!=no and geometry:polygon",
        "indicators": ["mapping-saturation", "currentness", "attribute-completeness"],
        "ratio_filter": (
            "building=* and building!=no and geometry:polygon and height=* or "
            + "building:levels=*"
        ),
        "project": "core",
        "source": None,  # TODO: Should not be in response if None
    }


@pytest.fixture
def metadata_indicator_mapping_saturation():
    return {
        "name": "Mapping Saturation",
        "description": (
            "Calculate if mapping has saturated. High saturation has been reached if "
            + "the growth of the fitted curve is minimal."
        ),
        "project": "core",
    }


@pytest.fixture
def metadata_topic_minimal():
    return {
        "key": "minimal",
        "name": "Minimal",
        "description": "A minimal topic definition for testing purposes",
        "endpoint": "elements/count",
        "filter": "building=* and building!=no and geometry:polygon",
        "indicators": ["minimal"],
        "ratio_filter": None,  # TODO: Should not be in response if None
        "project": "misc",
        "source": None,  # TODO: Should not be in response if None
    }


@pytest.fixture
def metadata_indicator_minimal():
    return {
        "name": "Minimal",
        "description": "An minimal Indicator for testing purposes.",
        "project": "misc",
    }


@pytest.fixture
def metadata_report_minimal():
    return {
        "name": "Minimal",
        "description": (
            "This report shows the quality for two indicators: Mapping Saturation and "
            + "Currentness. It's main function is to test the interactions between "
            + "database, api and website."
        ),
        "project": "misc",
    }
