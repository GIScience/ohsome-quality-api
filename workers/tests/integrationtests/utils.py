import inspect
import os

import vcr
from schema import Optional, Or, Schema

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures", "vcr_cassettes")


def filename_generator(function):
    """Return filename of function source file with the appropriate file-ending."""
    filename = os.path.basename(inspect.getsourcefile(function))
    return os.path.splitext(filename)[0] + "." + oqt_vcr.serializer


oqt_vcr = vcr.VCR(
    serializer="json",
    cassette_library_dir=FIXTURE_DIR,
    record_mode="new_episodes",
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    func_path_generator=filename_generator,
)


api_schema_indicator = Schema(
    {
        "attribution": {
            "url": str,
            "text": str,
        },
        "apiVersion": str,
        "metadata": {
            "name": str,
            "requestUrl": str,
            "description": str,
        },
        "layer": {
            "name": str,
            "description": str,
            "endpoint": str,
            "filter": str,
            Optional("ratio_filter"): Or(str, None),
        },
        "result": {
            "timestamp_oqt": str,
            "timestamp_osm": Or(str, None),
            "value": Or(float, None),
            "label": str,
            "description": str,
            "svg": str,
            Optional("data"): Or(dict, None),
        },
    }
)

api_schema_report = Schema(
    {
        "attribution": {
            "url": str,
            "text": str,
        },
        "apiVersion": str,
        "metadata": {
            "name": str,
            "description": str,
            "requestUrl": str,
        },
        "result": {
            "value": float,
            "label": str,
            "description": str,
        },
        "indicators": {
            str: {
                "metadata": {
                    "name": str,
                    "description": str,
                },
                "layer": {
                    "name": str,
                    "description": str,
                    "endpoint": str,
                    "filter": str,
                    Optional("ratio_filter"): Or(str, None),
                },
                "result": {
                    "timestamp_oqt": str,
                    "timestamp_osm": Or(str, None),
                    "value": Or(float, None),
                    "label": str,
                    "description": str,
                    "svg": str,
                    Optional("data"): Or(dict, None),
                },
            }
        },
    }
)
