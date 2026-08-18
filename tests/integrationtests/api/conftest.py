import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from ohsome_quality_api import __version__
from ohsome_quality_api.api.api import app
from ohsome_quality_api.geodatabase.client import set_pool_for_request


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        "ohsome_quality_api.geodatabase.client.set_pool_for_request",
        lambda _: None,
    )

    def set_pool_for_request_(request: Request):
        yield

    app.dependency_overrides[set_pool_for_request] = set_pool_for_request_
    yield TestClient(app)


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
def metadata_topic_building_count():
    return {
        "building-count": {
            "name": "Buildings (count)",
            "description": "All buildings as defined by all objects tagged with 'building=*'.",  # noqa
            "aggregationType": "count",
            "filter": "building=* and building!=no and geometry:polygon",
            "indicators": [
                "mapping-saturation",
                "currentness",
                "attribute-completeness",
                "user-activity",
            ],
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
            "qualityDimension": "completeness",
        }
    }


@pytest.fixture
def metadata_quality_dimension():
    return {
        "completeness": {
            "name": "completeness",
            "description": "The degree to which subject data associated "
            "with an entity has values for all expected "
            "attributes and related entity instances in "
            "a specific context of use.",
            "source": "https://www.iso.org/standard/78900.html",
        }
    }


@pytest.fixture
def metadata_attribute_forests():
    return {
        "forests": {
            "leaf-type": {
                "filter": "leaf_type=*",
                "name": "Leaf Type",
                "description": "TODO",
            }
        }
    }
