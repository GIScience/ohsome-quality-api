import filecmp
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

import plotly.graph_objects as pgo
from approvaltests.reporters.first_working_reporter import FirstWorkingReporter
from approvaltests.reporters.generic_diff_reporter import GenericDiffReporter
from approvaltests.reporters.generic_diff_reporter_config import (
    GenericDiffReporterConfig,
)
from approvaltests.reporters.python_native_reporter import PythonNativeReporter
from approvaltests.reporters.report_with_diff_command_line import (
    ReportWithDiffCommandLine,
)


class BlockingGenericDiffReporter(GenericDiffReporter):
    @staticmethod
    def run_command(command_array: list[str]):
        # Use run instead of Popen which waits for process to finish
        subprocess.run(command_array)  # noqa: S603

    def report(self, *args, **kwargs) -> bool:
        # Wrap report func to catch failure of programs which open/start other
        # programs like `open` on MacOS and `xdg-open` on Linux
        try:
            return super().report(*args, **kwargs)
        except subprocess.CalledProcessError:
            return False


class ReportWithPyCharmLinuxFlatpak(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmLinuxFlatpak",
                path="/usr/bin/flatpak",
                extra_args=["run", "com.jetbrains.PyCharm-Community", "diff"],
            )
        )


class ReportWithPyCharmLinux(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmLinux",
                path="pycharm",
                extra_args=["diff"],
            )
        )


class ReportWithVSCodeLinux(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithVSCodeLinux",
                path="/usr/bin/code",
                extra_args=["--new-window", "--wait", "--diff"],
            )
        )


class ReportWithPyCharmProfessionalMacOS(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmProfessionalMacOS",
                # Use open to block Python until diff tool is closed again
                path="/usr/bin/open",
                extra_args=[
                    # -W: Wait until the application is closed
                    "-W",
                    # -n: new instance
                    "-n",
                    # -a: application
                    "-a",
                    "/Applications/PyCharm Professional Edition.app/Contents/MacOS/pycharm",  # noqa
                    "--args",
                    "diff",
                ],
            )
        )


class ReportWithPyCharmCommunityMacOS(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmCommunityMacOS",
                # Use open to block Python until diff tool is closed again
                path="/usr/bin/open",
                extra_args=[
                    # -W: Wait until the application is closed
                    "-W",
                    # -n: New instance
                    "-n",
                    # -a: Application
                    "-a",
                    "/Applications/PyCharm CE.app/Contents/MacOS/pycharm",
                    "--args",
                    "diff",
                ],
            )
        )


class ReportWithVSCodeMacOS(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithVSCodeMacOS",
                # Use open to block Python until diff tool is closed again
                path="/usr/bin/open",
                extra_args=[
                    # -W: Wait until the application is closed
                    "-W",
                    # -n: New instance
                    "-n",
                    # -a: Application
                    "-a",
                    "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",  # noqa
                    "--args",
                    "--new-window",
                    "--wait",
                    "--diff",
                ],
            )
        )


class PlotlyDiffReporter(FirstWorkingReporter):
    """Report the image representation of Plotly figures using diff tools.

    Plotly figures are compared using the JSON representation.
    This reporter reports the difference by showing the image representation of
    the Plotly figures in a diff tool.
    """

    # TODO: Maybe it is better to open images in diff tools and afterwards the
    # JSONs as well. Approval happens through diff tool show JSONs. This way no
    # moving of files (approving) in the reporter class necessary.

    def __init__(self):
        if platform.system() == "Linux":
            self.reporters = (
                ReportWithPyCharmLinux(),
                ReportWithPyCharmLinuxFlatpak(),
                ReportWithVSCodeLinux(),
            )
        elif platform.system() == "Darwin":
            self.reporters = (
                ReportWithPyCharmProfessionalMacOS(),
                ReportWithPyCharmCommunityMacOS(),
                ReportWithVSCodeMacOS(),
            )
        else:
            # Will return False for when calling `report`
            self.reporters = []
        super().__init__(*self.reporters)

    def report(self, received_path: str, approved_path: str) -> bool:
        approved_path_image = str(Path(approved_path).with_suffix(".png"))
        received_path_image = str(Path(received_path).with_suffix(".png"))
        if os.path.exists(approved_path):
            with open(approved_path, "r") as file:
                raw = json.load(file)
            approved_figure = pgo.Figure(raw)
            approved_figure.write_image(approved_path_image)
        else:
            shutil.copyfile(
                Path(__file__).parent / "fixtures" / "empty.png",
                approved_path_image,
            )

        with open(received_path, "r") as file:
            raw = json.load(file)
        received_figure = pgo.Figure(raw)
        received_figure.write_image(received_path_image)

        try:
            # If images are equal before opening diff tool, then difference is
            # JSON specific and is not reflected in image representation.
            if filecmp.cmp(received_path_image, approved_path_image):
                return FirstWorkingReporter(
                    *self.reporters,
                    ReportWithDiffCommandLine(),
                    PythonNativeReporter(),
                ).report(received_path, approved_path)
            else:
                success = super().report(received_path_image, approved_path_image)
                if success:
                    # After diff tool is closed are the images the same?
                    if filecmp.cmp(received_path_image, approved_path_image):
                        # The diff tools saves approved image but we also need to
                        # create approved file for the JSON representation
                        shutil.move(received_path, approved_path)
                else:
                    # Fallback to reporting JSON difference
                    return FirstWorkingReporter(
                        *self.reporters,
                        ReportWithDiffCommandLine(),
                        PythonNativeReporter(),
                    ).report(received_path, approved_path)
        finally:
            try:
                os.remove(received_path_image)
            except FileNotFoundError:
                pass
            try:
                os.remove(approved_path_image)
            except FileNotFoundError:
                pass
        return success
