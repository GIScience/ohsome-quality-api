import inspect
import os

import vcr

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
