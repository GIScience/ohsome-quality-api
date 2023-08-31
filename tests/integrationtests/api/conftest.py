import pytest
from fastapi.testclient import TestClient

from ohsome_quality_api import __version__
from ohsome_quality_api.api.api import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def response_template():
    return {
        "apiVersion": __version__,
        "attribution": {
            "url": (
                "https://github.com/GIScience/ohsome-quality-api/blob/main/"
                + "COPYRIGHTS.md"
            ),
        },
    }


@pytest.fixture
def response_metadata_topic_building_count():
    return {
        "building-count": {
            "name": "Building Count",
            "description": "All buildings as defined by all objects tagged with 'building=*'.",  # noqa
            "endpoint": "elements",
            "aggregationType": "count",
            "filter": "building=* and building!=no and geometry:polygon",
            "indicators": [
                "mapping-saturation",
                "currentness",
                "attribute-completeness",
            ],
            "projects": ["core"],
            "source": None,
        },
    }


@pytest.fixture
def metadata_indicator_mapping_saturation():
    return {
        "mapping-saturation": {
            "name": "Mapping Saturation",
            "description": (
                "Calculate if mapping has saturated. High saturation has been reached "
                + "if the growth of the fitted curve is minimal."
            ),
            "projects": [
                "core",
                "corine-land-cover",
                "expanse",
                "experimental",
                "idealvgi",
                "mapaction",
                "sketchmap",
            ],
            "qualityDimension": "completeness",
        }
    }


@pytest.fixture
def metadata_report_multilevel_mapping_saturation():
    return {
        "multilevel-mapping-saturation": {
            "name": "Multilevel Mapping Saturation",
            "description": "This report shows the mapping saturation of four major "
            + "Map Features (https://wiki.openstreetmap.org/wiki/Map_features): "
            + "buildings, land-use/land-cover, points of interest and infrastructure. "
            + "It evolved from the OSM Element Vectorisation tool (https://gitlab."
            + "gistools.geog.uni-heidelberg.de/giscience/ideal-vgi/osm-element-"
            + "vectorisation).",
            "projects": ["core"],
        }
    }


@pytest.fixture
def metadata_quality_dimension_completeness():
    return {
        "completeness": {
            "name": "Completeness",
            "description": "something that is still a TODO",
        }
    }


@pytest.fixture
def metadata_project_core():
    return {
        "core": {
            "name": "TODO",
            "description": "something that is still a TODO",
        }
    }


@pytest.fixture
def metadata_topic_minimal():
    return {
        "minimal": {
            "key": "minimal",
            "name": "Minimal",
            "description": "A minimal topic definition for testing purposes",
            "endpoint": "elements",
            "aggregationType": "count",
            "filter": "building=* and building!=no and geometry:polygon",
            "indicators": ["minimal"],
            "ratioFilter": None,  # TODO: Should not be in response if None
            "projects": ["misc"],
            "source": None,  # TODO: Should not be in response if None
        }
    }


@pytest.fixture
def metadata_indicator_minimal():
    return {
        "minimal": {
            "name": "Minimal",
            "description": "An minimal Indicator for testing purposes.",
            "projects": ["misc"],
            "qualityDimension": "minimal",
        }
    }


@pytest.fixture
def metadata_report_minimal():
    return {
        "minimal": {
            "name": "Minimal",
            "description": (
                "This report shows the quality for two indicators: Mapping Saturation "
                + "and Currentness. It's main function is to test the interactions "
                + "between database, api and dashboard."
            ),
            "projects": ["misc"],
        }
    }
