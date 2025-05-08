import inspect
import os
from unittest.mock import MagicMock

import geojson
import vcr

from ohsome_quality_api.topics.definitions import get_topic_preset
from ohsome_quality_api.topics.models import TopicDefinition

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures")
VCR_DIR = os.path.join(FIXTURE_DIR, "vcr_cassettes")


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def filename_generator(function):
    """Return filename of function source file with the appropriate file-ending."""
    test_path = inspect.getsourcefile(function)
    # path relative to TEST_DIR
    rel_test_path = os.path.relpath(os.path.dirname(test_path), TEST_DIR)
    filename_base = os.path.splitext(os.path.basename(test_path))[0]
    return os.path.join(rel_test_path, filename_base + "." + oqapi_vcr.serializer)


def get_current_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_fixture_dir():
    return os.path.join(get_current_dir(), "fixtures")


def get_geojson_fixture(name):
    path = os.path.join(get_fixture_dir(), name)
    with open(path, "r") as f:
        return geojson.load(f)


def get_topic_fixture(name: str) -> TopicDefinition:
    return get_topic_preset(name)


# usage example:
# add this as parameter to vcr.VCR:
#   before_record_response=replace_body(["image/png"], dummy_png),
def replace_body(content_types, replacement):
    def before_record_response(response):
        # header keys are sometimes in camel case
        response["headers"] = {k.lower(): v for k, v in response["headers"].items()}
        if any(ct in content_types for ct in response["headers"]["content-type"]):
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

oqapi_vcr = vcr.VCR(
    cassette_library_dir=VCR_DIR,
    # details see https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    record_mode=os.getenv("VCR_RECORD_MODE", default="new_episodes"),
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    func_path_generator=filename_generator,
    before_record_response=replace_body(["image/png"], dummy_png),
    # ignore github.com. ApprovalTests
    ignore_hosts=["testserver", "github"],
    ignore_localhost=True,  # do not record HTTP requests to local FastAPI test instance
)
