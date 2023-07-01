import os

import pytest

from tests.integrationtests.utils import get_fixture_dir


@pytest.fixture(scope="class")
def mock_env_oqt_data_dir():
    directory = os.path.join(get_fixture_dir(), "rasters")
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("OQT_DATA_DIR", directory)
        yield mp
