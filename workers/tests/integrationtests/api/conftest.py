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
                + "data/COPYRIGHTS.md"
            ),
        },
    }
