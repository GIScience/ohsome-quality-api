import os

import vcr

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures", "vcr_cassettes")

oqt_vcr = vcr.VCR(
    serializer="json",
    cassette_library_dir=FIXTURE_DIR,
    record_mode="new_episodes",
)
