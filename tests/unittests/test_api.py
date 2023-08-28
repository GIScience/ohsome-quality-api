from ohsome_quality_api import __version__ as oqt_version
from ohsome_quality_api.api.api import empty_api_response


def test_empty_api_response():
    response_template = {
        "apiVersion": oqt_version,
        "attribution": {
            "url": (
                "https://github.com/GIScience/ohsome-quality-analyst/blob/main/"
                + "COPYRIGHTS.md"
            ),
        },
    }
    assert response_template == empty_api_response()
