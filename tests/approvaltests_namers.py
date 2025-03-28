import os
from pathlib import Path

from approvaltests.namer.namer_base import NamerBase

TEST_DIR = Path(__file__).parent
APPROVED_DIR = TEST_DIR / "approvals"


class PytestNamer(NamerBase):
    def __init__(self, extension=None):
        """An approval tests Namer for naming approved and received files.

        These files will get stored under:
        `tests/approval/{module}/test_file.py--TestClass--test_func[a]`

        This class uses the `PYTEST_CURRENT_TEST` environment variable, which
        consist of the node ID and the current stage:
        `relative/path/to/test_file.py::TestClass::test_func[a] (call)`

        During a pytest test session, stages can be setup, teardown or call.
        Approval tests should only be used during the call stage and therefore
        the ` (call)` postfix is removed.

        To avoid the forbidden character `:` in system paths, it is replaced by `-`.
        """
        self.nodeid: Path = Path(os.environ["PYTEST_CURRENT_TEST"])
        NamerBase.__init__(self, extension)

    def get_file_name(self) -> Path:
        """File name is pytest nodeid w/out directory name and pytest stage."""
        return Path(str(self.nodeid.name).replace(" (call)", "").replace("::", "-"))

    def get_directory(self) -> Path:
        """Directory is `tests/approval/{module}` derived from pytest nodeid."""
        parts = self.nodeid.parent.parts
        directory = Path(*[p for p in parts if p not in ["tests"]])
        return APPROVED_DIR / directory

    def get_config(self) -> dict:
        return {}
