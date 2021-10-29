import inspect
import os
from unittest.mock import MagicMock

import geojson
import vcr

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures", "vcr_cassettes")


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def filename_generator(function):
    """Return filename of function source file with the appropriate file-ending."""
    filename = os.path.basename(inspect.getsourcefile(function))
    return os.path.splitext(filename)[0] + "." + oqt_vcr.serializer


def get_geojson_fixture(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", name)
    with open(path, "r") as f:
        return geojson.load(f)


oqt_vcr = vcr.VCR(
    serializer="json",
    cassette_library_dir=FIXTURE_DIR,
    # details see https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    record_mode=os.getenv("VCR_RECORD_MODE", default="new_episodes"),
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    func_path_generator=filename_generator,
)
