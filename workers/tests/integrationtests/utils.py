import inspect
import os
from unittest.mock import MagicMock

import geojson
import vcr

from ohsome_quality_analyst.base.layer import LayerDefinition
from ohsome_quality_analyst.definitions import get_layer_definition

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures", "vcr_cassettes")


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def filename_generator(function):
    """Return filename of function source file with the appropriate file-ending."""
    filename = os.path.basename(inspect.getsourcefile(function))
    return os.path.splitext(filename)[0] + "." + oqt_vcr.serializer


def get_current_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_fixture_dir():
    return os.path.join(get_current_dir(), "fixtures")


def get_geojson_fixture(name):
    path = os.path.join(get_fixture_dir(), name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_layer_fixture(name: str) -> LayerDefinition:
    return get_layer_definition(name)


# usage example:
# add this as parameter to vcr.VCR:
#   before_record_response=replace_body(["image/png"], dummy_png),
def replace_body(content_types, replacement):
    def before_record_response(response):
        if any(ct in content_types for ct in response["headers"]["Content-Type"]):
            response["body"]["string"] = replacement
        return response

    return before_record_response


# dummy_png created with PIL and this command:
# >>> output = io.BytesIO()
# >>> Image.new("RGB", (1, 1)).save(output, format="PNG")
# >>> output.getvalue()
dummy_png = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\02\x00"
    b"\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)

oqt_vcr = vcr.VCR(
    cassette_library_dir=FIXTURE_DIR,
    # details see https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    record_mode=os.getenv("VCR_RECORD_MODE", default="new_episodes"),
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    func_path_generator=filename_generator,
    before_record_response=replace_body(["image/png"], dummy_png),
)
