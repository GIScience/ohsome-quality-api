import os
from pathlib import Path
from typing import Dict

from approvaltests.namer.namer_base import NamerBase


class PytestNamer(NamerBase):
    def __init__(self, extension: str = ".txt", postfix: str = ""):
        """An approval tests Namer for naming approved and received files.

        This Namer uses the `PYTEST_CURRENT_TEST` environment variable, which
        consist of the node ID and the current stage to derive names:
        `relative/path/to/test_file.py::TestClass::test_func[a] (call)`

        Above example will be translated to:
        `relative/path/to/test_file.py--TestClass--test_func[a]`

        Following changes are applied to the `PYTEST_CURRENT_TEST` environmen
        variables:
            - To avoid the forbidden character `:` in system paths, it is
              replaced by `-`.
            - During a pytest test session, stages can be setup, teardown or
              call. Approval tests should only be used during the call stage
              and therefore the ` (call)` postfix is removed.

        If verify is called multiple times use `postfix` parameter to
        differentiate names.
        """
        self.nodeid: Path = Path(os.environ["PYTEST_CURRENT_TEST"])
        self.postfix = postfix
        NamerBase.__init__(self, extension)

    def get_file_name(self) -> Path:
        """File name is pytest nodeid w/out directory name and pytest."""
        file_name = str(self.nodeid.name).replace(" (call)", "").replace("::", "-")
        return Path(file_name) / self.postfix

    def get_directory(self) -> Path:
        """Directory is `tests/approval/{module}` derived from pytest nodeid."""
        base_dir = Path(__file__).parent / "approvals"
        parts = self.nodeid.parent.parts
        directory = Path(*[p for p in parts if p not in ["tests"]])
        return base_dir / directory

    def get_config(self) -> Dict[str, str]:
        return {}
