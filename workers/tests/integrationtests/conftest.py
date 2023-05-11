import os

import pytest

from tests.integrationtests.utils import get_fixture_dir


@pytest.fixture()
def mock_env_oqt_data_dir(monkeypatch):
    directory = os.path.join(get_fixture_dir(), "rasters")
    monkeypatch.setenv("OQT_DATA_DIR", directory)
